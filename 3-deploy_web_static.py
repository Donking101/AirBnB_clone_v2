#!/usr/bin/python3
"""
Fabric script to create and distribute an archive to web servers.
"""

from fabric.api import env, local, run, put
from os.path import exists
from datetime import datetime

# Set the username and SSH key from command line
env.user = 'ubuntu'
env.key_filename = ['~/.ssh/id_rsa']

# Define the IP addresses of the web servers
env.hosts = ['100.25.30.13', '54.90.11.15']

def do_pack():
    """
    Create a compressed archive of the web_static folder.

    Returns:
        (str): Path to the created archive or None if failed.
    """
    try:
        time_format = "%Y%m%d%H%M%S"
        time_now = datetime.now().strftime(time_format)
        archive_path = "versions/web_static_{}.tgz".format(time_now)
        local("mkdir -p versions")
        local("tar -cvzf {} web_static".format(archive_path))
        return archive_path
    except Exception as e:
        print("Error:", e)
        return None

def do_deploy(archive_path):
    """
    Distribute the archive to the web servers.

    Args:
        archive_path (str): Path to the archive file.

    Returns:
        (bool): True if deployment successful, False otherwise.
    """
    if not exists(archive_path):
        return False
    try:
        file_name = archive_path.split('/')[1]
        file_name_without_extension = file_name.split('.')[0]
        remote_path = "/tmp/{}".format(file_name)
        put(archive_path, "/tmp/")
        run("mkdir -p /data/web_static/releases/{}/".format(file_name_without_extension))
        run("tar -xzf {} -C /data/web_static/releases/{}/".format(remote_path, file_name_without_extension))
        run("rm {}".format(remote_path))
        run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(file_name_without_extension, file_name_without_extension))
        run("rm -rf /data/web_static/releases/{}/web_static".format(file_name_without_extension))
        run("rm -rf /data/web_static/current")
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(file_name_without_extension))
        return True
    except Exception as e:
        print("Error:", e)
        return False

def deploy():
    """
    Deploy the compressed archive to the web servers.

    Returns:
        (bool): True if deployment successful, False otherwise.
    """
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

if __name__ == "__main__":
    deploy()
