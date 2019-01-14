#
# Copyright 2019 University of Technology, Sydney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#   * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
#     the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import sys
import os


def authenticate(sgtk):
    """

    Args:
        sgtk:

    Returns:

    """

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


def import_sgtk():
    """

    Returns:

    """
    sgtk_location = os.environ['SHARED_TANK_PATH']
    sys.path.append(sgtk_location)
    import sgtk
    return sgtk
