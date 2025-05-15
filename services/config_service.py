from services.logger import loggie

def reset_configuration():
    """Resets system configuration."""
    loggie.info("Resetting configuration")
    # db.drop_all()
    # db.create_all()

def initialize_configuration():
    """Initializes system configuration."""
    loggie.info("Started config initialization")