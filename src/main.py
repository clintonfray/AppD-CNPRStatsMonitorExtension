import requests
from requests.auth import HTTPBasicAuth
import yaml
import logging
from urllib3.exceptions import InsecureRequestWarning
import yamale
from yamale import YamaleError


# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logging.basicConfig(format=' %(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', filename='cpnr_app.log', level=logging.INFO)

def read_config():

    # YAML Schema Validation
    try:
        file_schema = yamale.make_schema('./schema.yaml')
        file_config = yamale.make_data('./config.yaml')

        yamale.validate(file_schema, file_config)
        
        logging.info('Validation success! 👍')

    except YamaleError as e:
        print('Validation failed!')
        for result in e.results:
            print('------------')
            print(f"Error validating data {result.data}")
            logging.error('------------')
            logging.error(f"Error validating data {result.data}")
            for error in result.errors:
                print(f'\t{error}')
                logging.error(f'\t{error}')
        exit(1)
    except:
        logging.error('Exception: We could not validate the config.yaml file!')
        exit(1)

    # Set Global Variables
    global config
    global api_user
    global api_pass
    global api_hostname
    global api_port
    global request_timeout

    try:
        file_config_import = open('./config.yaml', 'r')
        config = yaml.safe_load(file_config_import)
        file_config_import.close()
    except Exception as e:
        logging.error(
            f'Exception: Unable to import the config.yaml file!, {e}')
        exit(1)

    stats = config.get('stats')

    api_hostname = stats['endpoint']['hostname']
    api_port = stats['endpoint']['port']

    api_user = stats['auth']['user']
    api_pass = stats['auth']['pass']

    request_timeout = 10


def get_cpnr_stats():
    try:
        basic_auth = HTTPBasicAuth(api_user, api_pass)

        headers = {'Accept': 'application/json'}
        url = f'https://{api_hostname}:{api_port}/web-services/rest/stats/DNSCachingServer'

        response = requests.get(
            url, headers=headers, auth=basic_auth, verify=False, timeout=request_timeout)
        response.raise_for_status()
        results = response.json()

        metric_list = config.get('metrics')

        for m in metric_list:

            try:
                metric_name = m['name']
                metric_alias = m['alias']

                aggregation_type = m['aggregationType']
                time_rollup_type = m['timeRollUpType']

                try:
                    metric_value = int(results[metric_name])
                    try:
                        print(
                            f"name=Custom Metrics|DNSCachingServer|{metric_alias},aggregator={aggregation_type},time-rollup={time_rollup_type},value={metric_value}")
                        logging.info(
                            f"name=Custom Metrics|DNSCachingServer|{metric_alias},aggregator={aggregation_type},time-rollup={time_rollup_type},value={metric_value}")

                    except Exception as error:
                        logging.error('__________')
                        print(error)
                        logging.error(
                            f"Error occurred: The value is not a 64bit Integer. Metric Name: {metric_name}, Metric Value: {metric_value}")
                except Exception as error:
                    logging.error(
                        f'Exception: Unable to retrieve the Metric: {metric_name}')
                    logging.error('__________')

            except Exception as error:
                logging.error(
                    f'The metric name was not specified. Please check the config file.')
        return
    except Exception as error_message:
        logging.error('Error occurred:' + str(error_message))
        logging.error('Program Exit')
        exit(1)


if __name__ == "__main__":
    read_config()
    get_cpnr_stats()
