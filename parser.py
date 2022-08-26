import logging
import requests
import sys
import os
import datetime
import json

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s[line:%(lineno)d] [%(threadName)s] %(levelname)s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


API_ADDRESS = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=10&nc=1612409408851&pid=hp&FORM=BEHPTB&uhd=1&uhdwidth=3840&uhdheight=2160"
BASIC_URL = "https://cn.bing.com"


def main():
    response = requests.get(API_ADDRESS)
    res_data = response.json()
    for image in res_data['images']:
        startdate = image['startdate']

        # create directory
        dirname = os.getcwd() + '/pictures/' + startdate[:6]
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        pic_url = BASIC_URL + image['url']
        # download picture
        pic_filename = "{}/{}.jpg".format(dirname, startdate)
        if not os.path.exists(pic_filename):
            pic_res = requests.get(pic_url)
            with open(pic_filename, 'wb') as f:
                f.write(pic_res.content)

            logger.info("download picture:{}".format(pic_filename))
        else:
            logger.info("picture exists, ignore:{}".format(pic_filename))

        # process metadata
        image['url'] = BASIC_URL + image['url']
        image['urlbase'] = BASIC_URL + image['urlbase']
        image['copyrightlink'] = BASIC_URL + image['copyrightlink']
        image['quiz'] = BASIC_URL + image['quiz']
        image['p_path'] = "/pictures/{}/{}.jpg".format(startdate[:6], startdate)

        metadata_filename = dirname + '/metadata.json'
        path_exists = os.path.exists(metadata_filename)
        if not path_exists:
            with open(metadata_filename, 'w') as f:
                f.write(json.dumps({
                    "images": [
                        image
                    ],
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=4))
        else:
            with open(metadata_filename, 'r') as f:
                o_data = json.loads(f.read())
            with open(metadata_filename, 'w') as f:
                # judge exists
                exists = False
                for im in o_data['images']:
                    if image['startdate'] == im['startdate']:
                        exists = True

                if not exists:
                    o_data['images'].append(image)
                    o_data['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(json.dumps(o_data, ensure_ascii=False, indent=4))

        logger.info('write meta data:{}'.format(metadata_filename))


if __name__ == '__main__':
    main()
