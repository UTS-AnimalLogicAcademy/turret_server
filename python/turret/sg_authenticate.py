import os
import sys
sys.path.append('/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python')
import sgtk

TANK_PATH = "/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python"


def authenticate():

    if sgtk.get_authenticated_user():
        if not sgtk.get_authenticated_user().are_credentials_expired():
            print "Credentials already exist."
            return
            
    print "Authenticating credentials."

    # Import the ShotgunAuthenticator from the tank_vendor.shotgun_authentication
    # module. This class allows you to authenticate either interactively or, in this
    # case, programmatically.
    from tank_vendor.shotgun_authentication import ShotgunAuthenticator

    # Instantiate the CoreDefaultsManager. This allows the ShotgunAuthenticator to
    # retrieve the site, proxy and optional script_user credentials from shotgun.yml
    cdm = sgtk.util.CoreDefaultsManager()

    # Instantiate the authenticator object, passing in the defaults manager.
    authenticator = ShotgunAuthenticator(cdm)

    # Create a user programmatically using the script's key.
    user = authenticator.create_script_user(
        api_script="toolkit_user",
        api_key=os.getenv('SG_API_KEY')
    )

    # Tells Toolkit which user to use for connecting to Shotgun.
    sgtk.set_authenticated_user(user)

    cls._isAuthenticated = True


