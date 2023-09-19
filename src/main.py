from requests.auth import HTTPBasicAuth
import time
import requests
import urllib3
import yaml
import yamale
import logging
from libs.logging import log

urllib3.disable_warnings()


def main():

    global stats_hostname
    global stats_port
    global stats_username
    global stats_password
    global url_timeout

    try:
        # Get and Assign Configuration
        stats_config = load_app_config()

        stats_hostname = stats_config['stats']['endpoint']['hostname']
        stats_port = stats_config['stats']['endpoint']['port']
        stats_username = stats_config['stats']['auth']['user']
        stats_password = stats_config['stats']['auth']['pass']
        url_timeout = stats_config['defaultConfig']['api_timeout']
        wait_time = stats_config['defaultConfig']['wait_time']

        while True:

            results = api_stats_connector(hostname=stats_hostname, port=stats_port,
                                          username=stats_username, password=stats_password, verify=False, request_timeout=url_timeout)

            for metric in stats_config.get('metrics'):

                metric_name = metric['name']
                metric_alias = metric['alias']

                aggregation_type = metric['aggregationType']
                time_rollup_type = metric['timeRollUpType']

                try:

                    if metric.get(f'old_{metric_name}') is None:
                        # Add the metric to the metric object
                        metric[f'old_{metric_name}'] = int(
                            results[metric_name])
                    else:
                        try:
                            new_metric_value = int(results[metric_name])
                            prev_metric_value = metric[f'old_{metric_name}']
                            metric_value = new_metric_value - \
                                prev_metric_value

                            # Update Prev Metric with the updated meter
                            metric[f'old_{metric_name}'] = int(
                                results[metric_name])

                            log.info(
                                f"name=Custom Metrics|DNSCachingServer|{metric_alias},aggregator={aggregation_type},time-rollup={time_rollup_type},value={metric_value}")
                        except Exception as error:
                            log.error(
                                f"Error occurred: The value is not a 64bit Integer. Metric Name: {metric_name}, Metric Value: {metric_value}")
                except Exception as error:
                    log.error(
                        f'Exception: Unable to retrieve the Metric: {metric_name}')

            time.sleep(wait_time)

    except Exception as e:
        log.error(f'Error: {e}')


def api_stats_connector(hostname=None, port=None, username=None, password=None, request_timeout=10, verify=True):

    if (username is not None or password is not None):
        basic_auth = HTTPBasicAuth(username, password)
    else:
        basic_auth = None

    try:

        headers = {'Accept': 'application/json'}
        url = f'https://{hostname}:{port}/web-services/rest/stats/DNSCachingServer'

        response = requests.get(
            url, headers=headers, auth=basic_auth, verify=verify, timeout=request_timeout)

        response.raise_for_status()

    except Exception as e:
        raise Exception(f'API Connector Exception: {e}')

    return response.json()


def load_app_config():
    try:
        file_schema = yamale.make_schema('./schema.yaml')
        file_config = yamale.make_data('./config.yaml')

        yamale.validate(file_schema, file_config)

        log.info('Validation success! 👍')

    except yamale.YamaleError as e:
        log.error('Validation failed!')
        for result in e.results:
            raise Exception(f"Error validating data {result.data}")
    except:
        raise Exception(
            'Exception: We could not validate the config.yaml file!')

    try:
        file_config_import = open('./config.yaml', 'r')
        config = yaml.safe_load(file_config_import)
        file_config_import.close()
    except Exception as e:
        raise Exception(
            f'Exception: Unable to import the config.yaml file!, {e}')

    return config


if __name__ == '__main__':
    main()
