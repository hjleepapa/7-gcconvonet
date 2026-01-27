from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import hashlib
from extensions import db, ckeditor, bootstrap, migrate
import smtplib
from flask_socketio import SocketIO

# Sentry integration for error monitoring (optional)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Flask-SocketIO instance (will be initialized in create_app)
socketio = None

# --- Global Helper Functions & Configuration ---
def generate_gravatar_url(email, size=80, default_image='mp', rating='g'):
    """Generates a Gravatar URL for a given email address."""
    if email is None:
        email = ''
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default_image}&r={rating}"

load_dotenv()

# Initialize Sentry for error monitoring (optional)
if SENTRY_AVAILABLE:
    sentry_dsn = os.getenv('SENTRY_DSN')
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=None,
                    event_level=None
                ),
            ],
            traces_sample_rate=0.1,  # Reduced from 1.0 to save memory
            profiles_sample_rate=0.1,  # Reduced from 1.0 to save memory
            environment=os.getenv('RENDER_ENVIRONMENT', 'production') if os.getenv('RENDER') else 'development',
            release=os.getenv('RENDER_GIT_COMMIT', 'dev'),
        )
        print(f"✅ Sentry initialized: environment={os.getenv('RENDER_ENVIRONMENT', 'development')}")
    else:
        print("⚠️  Sentry DSN not configured - error monitoring disabled")
else:
    print("⚠️  Sentry not available - error monitoring disabled")

def create_app():
    global socketio
    
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Socket.IO for WebRTC voice
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

    # Register Blueprints (only essential ones for memory optimization)
    # Note: Convonet uses JWT authentication, not Flask-Login

    # Register Convonet blueprint (main functionality)
    from convonet.routes import convonet_todo_bp
    app.register_blueprint(convonet_todo_bp)
    
    # Register authentication and team collaboration blueprints
    from convonet.api_routes.auth_routes import auth_bp
    from convonet.api_routes.team_routes import team_bp
    from convonet.api_routes.team_todo_routes import team_todo_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(team_todo_bp)
    
    # Register WebRTC voice assistant blueprint
    from convonet.webrtc_voice_server_socketio import webrtc_bp, init_socketio
    app.register_blueprint(webrtc_bp)
    
    # Initialize Socket.IO event handlers
    init_socketio(socketio, app)

    # Main Application Routes
    @app.route('/', methods=["GET", "POST"])
    def home():
        msg_sent = False
        error_message = None
        if request.method == "POST":
            name = request.form.get("name")
            email_from = request.form.get("email")
            phone = request.form.get("phone")
            message_body = request.form.get("message")

            if not all([name, email_from, message_body]):
                error_message = "Please fill in all required fields (Name, Email, Message)."
            else:
                mail_server = os.environ.get('MAIL_SERVER')
                mail_port = int(os.environ.get('MAIL_PORT', 587))
                mail_username = os.environ.get('MAIL_USERNAME')
                mail_password = os.environ.get('MAIL_PASSWORD')
                mail_receiver = os.environ.get('MAIL_RECEIVER')

                if not all([mail_server, mail_username, mail_password, mail_receiver]):
                    print("Email configuration is incomplete for main contact form.")
                    error_message = "Message could not be sent due to a server configuration issue."
                else:
                    email_subject = f"New Contact Form Submission from {name} (Main Site)"
                    full_email_message = (
                        f"Subject: {email_subject}\n\n"
                        f"Name: {name}\nEmail: {email_from}\nPhone: {phone if phone else 'Not provided'}\n\nMessage:\n{message_body}\n"
                    )

                    try:
                        with smtplib.SMTP(mail_server, mail_port) as server:
                            server.starttls()
                            server.login(mail_username, mail_password)
                            server.sendmail(mail_username, mail_receiver, full_email_message.encode('utf-8'))
                        msg_sent = True
                    except Exception as e:
                        print(f"Error sending email from main contact form: {e}")
                        error_message = "An unexpected error occurred. Please try again later."

        return render_template('index.html', msg_sent=msg_sent, error=error_message)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/convonet-tech-spec')
    def convonet_tech_spec():
        """Renders the technical specification page for the Convonet todo project."""
        return render_template('convonet_tech_spec.html')
    
    @app.route('/convonet-system-architecture')
    def convonet_system_architecture():
        """Renders the System Architecture Diagram page for Convonet."""
        return render_template('convonet_system_architecture.html')
    
    @app.route('/convonet-sequence-diagram')
    def convonet_sequence_diagram():
        """Renders the Sequence Diagram page for Convonet."""
        return render_template('convonet_sequence_diagram.html')
    
    @app.route('/anthropic/team-dashboard')
    def team_dashboard():
        """Renders the team collaboration dashboard."""
        return render_template('team_dashboard.html')
    
    @app.route('/anthropic/register')
    def register():
        """Renders the user registration page."""
        return render_template('register.html')

    # Context Processors
    @app.context_processor
    def utility_processor():
        return dict(gravatar_url=generate_gravatar_url)

    return app

# Create the application instance for WSGI servers like Gunicorn to find.
app = create_app()

if __name__ == '__main__':
    # This is for local development only.
    socketio.run(app, debug=True, host='0.0.0.0', port=10000)