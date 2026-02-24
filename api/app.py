from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from urllib.parse import quote, urlparse, unquote, parse_qsl
import json
import os
import sys
import subprocess
import tempfile
import shutil
import tempfile  # 导入 tempfile 模块
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../templates')  # 指定模板文件夹的路径
app.secret_key = 'sing-box'  # 替换为实际的密钥
data_json = {}
os.environ['TEMP_JSON_DATA'] = '{"subscribes":[{"url":"URL","tag":"tag_1","enabled":true,"emoji":1,"subgroup":"","prefix":"","User-Agent":"v2rayng"},{"url":"URL","tag":"tag_2","enabled":false,"emoji":0,"subgroup":"命名/named","prefix":"❤️","User-Agent":"clashmeta"}],"auto_set_outbounds_dns":{"proxy":"","direct":""},"save_config_path":"./config.json","auto_backup":false,"exclude_protocol":"ssr","config_template":"","Only-nodes":false}'
data_json['TEMP_JSON_DATA'] = '{"subscribes":[{"url":"URL","tag":"tag_1","enabled":true,"emoji":1,"subgroup":"","prefix":"","User-Agent":"v2rayng"},{"url":"URL","tag":"tag_2","enabled":false,"emoji":0,"subgroup":"命名/named","prefix":"❤️","User-Agent":"clashmeta"}],"auto_set_outbounds_dns":{"proxy":"","direct":""},"save_config_path":"./config.json","auto_backup":false,"exclude_protocol":"ssr","config_template":"","Only-nodes":false}'

# 获取系统默认的临时目录路径
TEMP_DIR = tempfile.gettempdir()

"""
# 存储配置文件的过期时间（10分钟）
config_expiry_time = None
"""

def cleanup_temp_config():
    global config_expiry_time, config_file_path
    if config_expiry_time and datetime.now() > config_expiry_time:
        shutil.rmtree(os.path.dirname(config_file_path), ignore_errors=True)
        config_expiry_time = None
        config_file_path = None

# 获取临时 JSON 数据
def get_temp_json_data():
    temp_json_data = os.environ.get('TEMP_JSON_DATA')
    if temp_json_data:
        return json.loads(temp_json_data)
    return {}

# 获取config_template目录下的模板文件列表
def get_template_list():
    template_list = []
    config_template_dir = 'config_template'  # 配置模板文件夹路径
    template_files = os.listdir(config_template_dir)  # 获取文件夹中的所有文件
    template_list = [os.path.splitext(file)[0] for file in template_files if file.endswith('.json')]  # 移除扩展名并过滤出以.json结尾的文件
    template_list.sort()  # 对文件名进行排序
    return template_list

# 读取providers.json文件的内容，如果有临时 JSON 数据则使用它
def read_providers_json():
    temp_json_data = get_temp_json_data()
    if temp_json_data :
        return temp_json_data
    with open('providers.json', 'r', encoding='utf-8') as json_file:
        providers_data = json.load(json_file)
    return providers_data

# 写入providers.json文件的内容，如果有临时 JSON 数据则不写入
def write_providers_json(data):
    temp_json_data = get_temp_json_data()
    if not temp_json_data:
        with open('providers.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    template_list = get_template_list()
    template_options = [f"{index + 1}、{template}" for index, template in enumerate(template_list)]
    providers_data = read_providers_json()
    temp_json_data = get_temp_json_data()
    return render_template('index.html', template_options=template_options, providers_data=json.dumps(providers_data, indent=4, ensure_ascii=False), temp_json_data=json.dumps(temp_json_data, indent=4, ensure_ascii=False))

@app.route('/update_providers', methods=['POST'])
def update_providers():
    try:
        # 获取表单提交的数据
        new_providers_data = json.loads(request.form.get('providers_data'))
        # 更新providers.json文件
        write_providers_json(new_providers_data)
        flash('Providers.json文件已更新', 'success')
        flash('File Providers.json đã được cập nhật', 'Thành công^^')
    except Exception as e:
        flash(f'更新Providers.json文件时出错；{str(e)}', 'error')
        flash(f'Có lỗi khi cập nhật file Providers.json; {str(e)}', 'Lỗi!!!')
    return redirect(url_for('index'))

@app.route('/edit_temp_json', methods=['GET', 'POST'])
def edit_temp_json():
    if request.method == 'POST':
        try:
            new_temp_json_data = request.form.get('temp_json_data')
            print (new_temp_json_data)
            if new_temp_json_data:
                temp_json_data = json.loads(new_temp_json_data)
                os.environ['TEMP_JSON_DATA'] = json.dumps(temp_json_data, indent=4, ensure_ascii=False)
                #flash('TEMP_JSON_DATA 已更新', 'success')
                #flash('TEMP_JSON_DATA đã được cập nhật', 'Thành công^^')
                return jsonify({'status': 'success'})  # 返回成功状态
            else:
                return jsonify({'status': 'error', 'message': 'TEMP_JSON_DATA 不能为空(không thể trống)'}, content_type='application/json; charset=utf-8')  # 返回错误状态和消息
        except Exception as e:
            flash('TEMP_JSON_DATA 不能为空', 'error')
            flash('TEMP_JSON_DATA 格式出错：注意订阅链接末尾不要有换行，要在双引号""里面！！！')
            flash('TEMP_JSON_DATA không thể trống', 'Lỗi!!!')
            flash('Lỗi định dạng TEMP_JSON_DATA: lưu ý rằng liên kết đăng ký không được có ký tự xuống dòng ở cuối, mà phải nằm trong dấu ngoặc kép ""')
            flash('TEMP_JSON_DATA cannot be empty', 'error')
            flash(f'Error updating TEMP_JSON_DATA: note that the subscription link should not have a newline at the end, but should be inside double quotes ""')
            return jsonify({'status': 'error', 'message': str(e)})  # 返回错误状态和消息

def _normalize_scheme_slashes(value):
    if not value:
        return value
    index_of_colon = value.find(":")
    if index_of_colon == -1:
        return value
    next_char_index = index_of_colon + 2
    if next_char_index < len(value) and value[next_char_index] != "/":
        return value[:next_char_index - 1] + "/" + value[next_char_index - 1:]
    return value


def _extract_source_and_params(encoded_url, query_string):
    decoded_url = unquote(encoded_url)
    if query_string:
        return decoded_url, dict(parse_qsl(query_string, keep_blank_values=True))

    markers = ['&emoji=', '&file=', '&tag=', '&ua=', '&UA=', '&prefix=', '&eps=', '&enn=', '&gh=']
    marker_indexes = [decoded_url.find(marker) for marker in markers if marker in decoded_url]
    if marker_indexes:
        split_index = min(marker_indexes)
        source = decoded_url[:split_index]
        inline_query = decoded_url[split_index + 1:]
        return source, dict(parse_qsl(inline_query, keep_blank_values=True))

    return decoded_url, {}


def _build_subscribes(raw_sources, emoji_param, tag_param, ua_param, pre_param, enn_param):
    sources = [item.strip() for item in raw_sources.split('|') if item.strip()]
    subscribes = []

    emoji_value = int(emoji_param) if str(emoji_param).isdigit() else 1
    user_agent_value = ua_param or 'v2rayng'

    for idx, source in enumerate(sources, start=1):
        source = _normalize_scheme_slashes(unquote(source))
        if '/api/v4/projects/' in source:
            parts = source.split('/api/v4/projects/', 1)
            source = parts[0] + '/api/v4/projects/' + parts[1].replace('/', '%2F', 1)

        subscribe_item = {
            'url': source,
            'tag': tag_param if (idx == 1 and tag_param) else f'tag_{idx}',
            'enabled': True,
            'emoji': emoji_value,
            'subgroup': '',
            'prefix': pre_param or '',
            'ex-node-name': enn_param or '',
            'User-Agent': user_agent_value
        }
        subscribes.append(subscribe_item)

    return subscribes


def _collect_sources_and_params(url_from_path=None):
    allowed_params = {'emoji', 'file', 'tag', 'ua', 'UA', 'prefix', 'eps', 'enn', 'gh'}

    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        payload_params = {k: str(v) for k, v in payload.items() if k in allowed_params and v is not None}

        raw_sources = payload.get('sources')
        if raw_sources is None:
            raw_sources = payload.get('source')
        if raw_sources is None:
            raw_sources = payload.get('url')

        sources = []
        if isinstance(raw_sources, list):
            sources = [str(item).strip() for item in raw_sources if str(item).strip()]
        elif isinstance(raw_sources, str) and raw_sources.strip():
            if '|' in raw_sources:
                sources = [item.strip() for item in raw_sources.split('|') if item.strip()]
            else:
                sources = [raw_sources.strip()]

        return '|'.join(sources), payload_params

    if url_from_path:
        query_string = request.query_string.decode('utf-8')
        source_value, parsed_params = _extract_source_and_params(url_from_path, query_string)
        raw_sources = source_value.split('url=', 1)[-1] if source_value.startswith('url=') else source_value
        return raw_sources, parsed_params

    query_params = request.args.to_dict(flat=True)
    parsed_params = {k: query_params.get(k, '') for k in allowed_params}
    source_list = request.args.getlist('source')
    if not source_list:
        source_single = query_params.get('url', '')
        if source_single:
            source_list = [source_single]

    source_list = [item.strip() for item in source_list if item and item.strip()]
    return '|'.join(source_list), parsed_params


@app.route('/config', methods=['GET', 'POST'])
@app.route('/config/<path:url>', methods=['GET'])
def config(url=None):
    user_agent = request.headers.get('User-Agent')
    rua_values = os.getenv('RUA')
    if rua_values and any(rua_value in user_agent for rua_value in rua_values.split(',')):
        return Response(json.dumps({'status': 'error', 'message': 'block'}, indent=4, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=403)
    substrings = os.getenv('STR')
    if url and substrings and any(substring in url for substring in substrings.split(',')):
        return Response(json.dumps({'status': 'error', 'message_CN': 'invalid params'}, indent=4, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=403)

    temp_json_data = {
        'subscribes': [],
        'auto_set_outbounds_dns': {'proxy': '', 'direct': ''},
        'save_config_path': './config.json',
        'auto_backup': False,
        'exclude_protocol': 'ssr',
        'config_template': '',
        'Only-nodes': False
    }

    raw_sources, parsed_params = _collect_sources_and_params(url)

    emoji_param = parsed_params.get('emoji', '')
    file_param = parsed_params.get('file', '')
    tag_param = parsed_params.get('tag', '')
    ua_param = parsed_params.get('ua', '') or parsed_params.get('UA', '')
    pre_param = unquote(parsed_params.get('prefix', '')) if parsed_params.get('prefix') else ''
    eps_param = unquote(parsed_params.get('eps', '')) if parsed_params.get('eps') else ''
    enn_param = unquote(parsed_params.get('enn', '')) if parsed_params.get('enn') else ''
    gh_proxy_param = parsed_params.get('gh', '')

    raw_sources = _normalize_scheme_slashes(unquote(raw_sources)).replace(',', '%2C')
    subscribes = _build_subscribes(raw_sources, emoji_param, tag_param, ua_param, pre_param, enn_param)
    if not subscribes:
        return Response(
            json.dumps({'status': 'error', 'message': 'No subscription sources provided'}, indent=4, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=400
        )

    temp_json_data['subscribes'] = subscribes
    temp_json_data['exclude_protocol'] = eps_param if eps_param else temp_json_data.get('exclude_protocol', '')
    temp_json_data['config_template'] = unquote(file_param) if file_param else temp_json_data.get('config_template', '')
    temp_json_data['config_template'] = _normalize_scheme_slashes(temp_json_data['config_template'])

    try:
        selected_template_index = '0'
        selected_gh_proxy_index = ''
        if file_param.isdigit():
            temp_json_data['config_template'] = ''
            selected_template_index = str(int(file_param) - 1)
        if gh_proxy_param.isdigit():
            selected_gh_proxy_index = str(int(gh_proxy_param) - 1)
        temp_json_data = json.dumps(json.dumps(temp_json_data, indent=4, ensure_ascii=False), indent=4, ensure_ascii=False)
        subprocess.check_call([sys.executable, 'main.py', '--template_index', selected_template_index, '--temp_json_data', temp_json_data, '--gh_proxy_index', selected_gh_proxy_index])
        CONFIG_FILE_NAME = json.loads(os.environ['TEMP_JSON_DATA']).get('save_config_path', 'config.json')
        if CONFIG_FILE_NAME.startswith('./'):
            CONFIG_FILE_NAME = CONFIG_FILE_NAME[2:]
        config_file_path = os.path.join('/tmp/', CONFIG_FILE_NAME)
        if not os.path.exists(config_file_path):
            config_file_path = CONFIG_FILE_NAME
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads(data_json['TEMP_JSON_DATA']), indent=4, ensure_ascii=False)
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config_content = config_file.read()
            if config_content:
                flash('Configuration generated successfully', 'success')
                flash('Configuration generated successfully', 'success')
        json.loads(config_content)
        return Response(config_content, content_type='text/plain; charset=utf-8')
    except subprocess.CalledProcessError:
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads(data_json['TEMP_JSON_DATA']), indent=4, ensure_ascii=False)
        return Response(json.dumps({'status': 'error'}, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8', status=500)
    except Exception:
        return Response(json.dumps({'status': 'error', 'message_CN': 'Please check README and request parameters;', 'message_VN': 'Subscription parsing timeout: please check the subscription link, or switch to nogroupstemplate and try again; do not modify tag unless you know what it does;', 'message_EN': 'Subscription parsing timeout: Please check if the subscription link is correct or please change to "no_groups_template" and try again; Please do not modify the "tag" value unless you understand what it does;'}, indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8', status=500)


@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        selected_template_index = request.form.get('template_index')
        if not selected_template_index:
            flash('请选择一个配置模板', 'error')
            flash('Vui lòng chọn một mẫu cấu hình', 'Lỗi!!!')
            return redirect(url_for('index'))
        temp_json_data = json.dumps(os.environ['TEMP_JSON_DATA'], indent=4, ensure_ascii=False)
        # 修改这里：执行main.py并传递模板序号作为命令行参数，如果未指定，则传递空字符串
        subprocess.check_call([sys.executable, 'main.py', '--template_index', selected_template_index, '--temp_json_data', temp_json_data])
        CONFIG_FILE_NAME = json.loads(os.environ['TEMP_JSON_DATA']).get("save_config_path", "config.json")
        if CONFIG_FILE_NAME.startswith("./"):
            CONFIG_FILE_NAME = CONFIG_FILE_NAME[2:]
        # 设置配置文件的完整路径
        config_file_path = os.path.join('/tmp/', CONFIG_FILE_NAME) 
        if not os.path.exists(config_file_path):
            config_file_path = CONFIG_FILE_NAME  # 使用相对于当前工作目录的路径 
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads(data_json['TEMP_JSON_DATA']), indent=4, ensure_ascii=False)
        # 读取配置文件内容
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config_content = config_file.read()
            if config_content:
                flash('配置文件生成成功', 'success')
                flash('Tạo file cấu hình thành công', 'Thành công^^')
        config_data = json.loads(config_content)
        return Response(config_content, content_type='text/plain; charset=utf-8')
    except subprocess.CalledProcessError as e:
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads(data_json['TEMP_JSON_DATA']), indent=4, ensure_ascii=False)
        return Response(json.dumps({'status': 'error'}, indent=4,ensure_ascii=False), content_type='application/json; charset=utf-8', status=500)
    except Exception as e:
        #flash(f'Error occurred while generating the configuration file: {str(e)}', 'error')
        return Response(json.dumps({'status': 'error', 'message_CN': '认真看刚刚的网页说明、github写的reademe文件;', 'message_VN': 'Quá thời gian phân tích đăng ký: Vui lòng kiểm tra xem liên kết đăng ký có chính xác không hoặc vui lòng chuyển sang "nogroupstemplate" và thử lại; Vui lòng không chỉnh sửa giá trị "tag", trừ khi bạn hiểu nó làm gì;', 'message_EN': 'Subscription parsing timeout: Please check if the subscription link is correct or please change to "no_groups_template" and try again; Please do not modify the "tag" value unless you understand what it does;'}, indent=4,ensure_ascii=False), content_type='application/json; charset=utf-8', status=500)
    #return redirect(url_for('index'))

@app.route('/clear_temp_json_data', methods=['POST'])
def clear_temp_json_data():
    try:
        os.environ['TEMP_JSON_DATA'] = json.dumps({}, indent=4, ensure_ascii=False)
        flash('TEMP_JSON_DATA 已清空', 'success')
        flash('TEMP_JSON_DATA đã được làm trống', 'Thành công^^')
    except Exception as e:
        flash(f'清空 TEMP_JSON_DATA 时出错：{str(e)}', 'error')
        flash(f'Có lỗi khi làm trống TEMP_JSON_DATA: {str(e)}', 'Lỗi!!!')
    return jsonify({'status': 'success'})

"""
@app.route('/download_config', methods=['GET'])
def download_config():
    try:
        if config_file_path:
            # 清理临时配置文件
            #cleanup_temp_config()

            # 使用send_file发送文件
            return send_file(config_file_path, as_attachment=True)
        else:
            flash('配置文件不存在或已过期', 'error')
            flash('File cấu hình không tồn tại hoặc đã hết hạn', 'Lỗi!!!')
            return redirect(url_for('index'))
    except Exception as e:
        return str(e)  # 或者适当处理异常，例如返回一个错误页面
"""
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')