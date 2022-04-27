"""
COMP 593 - Final Project

Description:
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
"""
import ctypes
import hashlib
import json
from sys import argv, exit
from datetime import datetime, date
from os import path
import sqlite3
from http import client
import os
import time
import requests
def main():
    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(create_image_db('image.db'))

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)

    # Download today's APOD

    image_url = apod_info_dict['url']
    image_path = get_image_path(image_url, image_dir_path)
    image_msg = download_apod_image(image_url,image_path)
    image_sha256 = hashlib.sha256(image_msg.content).hexdigest()


    image_size = -1  # TODO


    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256, apod_info_dict)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)


def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')


def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()

    print("APOD date:", apod_date)
    return apod_date


def get_image_path(image_url, dir_path):
    today = time.strftime("%Y-%m-%d")

    l = image_url.split('/')[-1]

    image_path = os.path.join(dir_path, l)

    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    return (image_path)


def get_apod_info(date):

    cxn = client.HTTPSConnection('api.nasa.gov', 443)
    hard_key = "cwBAOk8bJtA7NivgO8oFCeLau1Gs8A69aOrhDI5L"
    demo_key = 'DEMO_KEY'
    key_input = input("Would you like to use a hardkey, demo key or your own key?  h/d/u")
    if key_input == 'h':
        cxn.request('GET', '/planetary/apod?api_key=' + hard_key + '&date=' + date)

    elif key_input == 'u':
        user_key = input("Enter your provided from APOD API")
        cxn.request('GET', '/planetary/apod?api_key=' + user_key + '&date=' + date)

    else:
        if key_input == 'd':
            cxn.request('GET', '/planetary/apod?api_key=' + demo_key + '&date=' + date)

    response = cxn.getresponse()
    if response.status == 200:
        print('Reponse:', response.status, 'is a valid code', '\n')
    else:
        print('Error', response.status, ' is not a valid code')
        print('Did you enter a valid api key?')

    json_image = response.read().decode()
    json_image = json.loads(json_image)




    """
    Gets information from the NASA API for the Astronomy
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """
    return json_image


def print_apod_info(image_url, image_size, image_sha256,image_path):
    print(image_size, ' bytes')
    print(image_path)
    print(image_url)
    print(image_sha256)


    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """



def download_apod_image(image_url,image_path):
    print(R"Downloading image from URL...", end='')
    response = requests.get(image_url)
    if response.status_code == 200:

            print('Success!')
    else:
        print('Download failed. Error', response.status_code)




    """
        Downloads an image from a specified URL.

        :param image_url: URL of image
        :returns: Response message that contains image data
        """
    return response


def save_image_file(image_msg, image_path):
    print("Saving File To Disk...")
    with open(image_path, 'wb') as file:
            file.write(image_msg.content)







    ''':param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    '''



def create_image_db(db_path):
    myConnection = sqlite3.connect(db_path)

    # Once we have a Connection object, we can generate a Cursor object, and use that to run our SQL Queries
    myCursor = myConnection.cursor()
    primaryquery = """CREATE TABLE IF NOT EXISTS APOD (
                                       'Date of Image' text NOT NULL,
                                       'Obtained Date' text NOT NULL,
                                       
                                       'File Path' text NOT NULL,
                                       'File Size' text NOT NULL,
                                       'SHA-256 value' text NOT NULL,
                                       'Image URL' text NOT NULL,
                                       'Explanation' text NOT NULL,
                                       'Copyright' text,
                                       PRIMARY KEY('Date of Image')
                                       );"""
    myCursor.execute(primaryquery)

    # This is the same syntax as the above example:

    myConnection.commit()
    myConnection.close()

    return db_path


def add_image_to_db(db_path, image_path, image_size, image_sha256, json_image,):
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    addQuery = """INSERT INTO APOD ('Date of Image',
                                          'Obtained Date',
                                          'File Path',
                                          'File Size',
                                          'SHA-256 value',
                                          'Image URL',
                                          'Explanation',
                                          'Copyright')
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
    today = time.strftime("%Y-%m-%d")
    data = (json_image['date'],
            today,
            image_path,
            image_size,
            image_sha256,
            json_image['url'],
            json_image['explanation'],
            json_image['copyright'])
    myCursor.execute(addQuery, data)
    myConnection.commit()
    myConnection.close()

    ''':param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    return  # TODO'''


def image_already_in_db(db_path, image_sha256):
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    hash_check = 'SELECT "File Path" FROM APOD WHERE "SHA-256 value" like "' + (image_sha256) + '";'
    myCursor.execute(hash_check)
    data = myCursor.fetchall()
    myConnection.commit()
    myConnection.close()

    if (data):
        return True

    else:

        return False






    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """
    return True


def set_desktop_background_image(image_path):

    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """



main()