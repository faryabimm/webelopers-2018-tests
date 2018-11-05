import sys
from ast import literal_eval
from datetime import datetime, timedelta
from threading import Thread

import requests
from flask import Flask, request, Response
from timeout_decorator import timeout, TimeoutError

import configuration as config
import logger
import tests

app = Flask(__name__)

group_status = {}


def test_and_set_active(group_id):
    if group_id not in group_status:
        group_status[group_id] = {
            'test_active': False,
            'test_count': 0,
            'last_run': None
        }

    if not group_status[group_id]['test_active']:
        group_status[group_id]['test_active'] = True
        group_status[group_id]['last_run'] = datetime.now()
        group_status[group_id]['test_count'] += 1
        return True
    elif datetime.now() - group_status[group_id]['last_run'] > timedelta(seconds=config.RUN_TIMEOUT_S):
        logger.log_info('releasing and reacquiring lock for group_id', group_id, 'due to run timeout')
        group_status[group_id]['last_run'] = datetime.now()
        group_status[group_id]['test_count'] += 1
        return True

    return False


def deactivate_status(group_id):
    group_status[group_id]['test_active'] = False


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    request_data = request.form
    if 'ip' not in request_data or 'group_id' not in request_data:
        logger.log_error('malformed post request data.')
        return Response('malformed post request data.')

    group_id = request_data['group_id']

    if test_and_set_active(group_id):
        logger.log_info('lock acquired for group_id', group_id)
        ip = request_data['ip']
        test_order = None
        if 'test_order' in request_data:
            logger.log_info('custom test order was given for group_id', group_id)
            test_order = literal_eval(request_data['test_order'])

        process_request(ip, group_id, test_order)
        logger.log_success('test for group_id', group_id, 'initiated successfully')
        return "success - test initiated"
    else:
        logger.log_error('another test for group_id', group_id, 'is in progress')
        return "error - existing test in progress"


def worker_run_tests(ip, test_order):
    test_results = {}
    if test_order is not None:
        for test_id in test_order:
            test_name = 'test_{}'.format(test_id)
            test_function = getattr(tests, test_name)

            try:
                test_result, string_output = run_test(test_function, ip)
            except TimeoutError:
                test_result, string_output = False, 'timeout'

            test_results[test_name] = test_result
            test_results['{}_log'.format(test_name)] = string_output

    else:
        for entry in dir(tests):
            if not entry.startswith('_'):
                test_function = getattr(tests, entry)

                try:
                    test_result, string_output = run_test(test_function, ip)
                except TimeoutError:
                    test_result, string_output = False, 'timeout'

                test_results[entry] = test_result
                test_results['{}_log'.format(entry)] = string_output

    return test_results


def worker_function(ip, group_id, test_order):
    logger.log_info('running tests for group_id', group_id, 'on ip address', ip)
    test_results = worker_run_tests(ip, test_order)
    logger.log_info('releasing lock for group_id', group_id)
    deactivate_status(group_id)
    logger.log_info('reporting test results for group_id', group_id, 'on ip address', ip, 'to competition server')
    report_test_results(group_id, test_results)
    logger.log_success('test for group_id', group_id, 'finished successfully')


def report_test_results(group_id, test_results):
    test_results['group_id'] = group_id
    requests.post('http://{}:{}'.format(config.REPORT_SERVER_HOST, config.REPORT_SERVER_PORT), test_results)


def process_request(ip, group_id, test_order):
    thread = Thread(target=worker_function, args=(ip, group_id, test_order))
    thread.start()


@timeout(config.TEST_TIMEOUT_S, use_signals=False)
def run_test(test_function, ip):
    result, string_output = test_function(
        # ip
    )
    return result, string_output


def runserver(port=config.PORT):
    app.run(host=config.HOST, port=port)


if __name__ == '__main__':
    # print(run_test(tests.test_7, None))
    if len(sys.argv) > 1:
        server_port = int(sys.argv[1])
        logger.log_info('starting server on custom port', server_port)
        runserver(server_port)
    else:
        logger.log_info('starting server on default port')
        runserver()
