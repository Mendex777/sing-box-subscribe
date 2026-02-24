# 操作说明去看[英文文档](https://github.com/Toperlock/sing-box-subscribe/blob/main/instructions/README.md)，中文文档操作说明不再提供

# 免责声明：sing-box-subscribe.vercel.app域名目前已被其他人占用，与本项目无关。后果自负
![image](https://github.com/Toperlock/sing-box-subscribe/assets/86833913/f9af80bc-f1b7-45dd-a2eb-e26910069f21)

### 使用 `/config/URL` 添加参数符号已修改，从原来的 `/&` 改为 `&`。有问题请提issue，不要打扰 `sing-box`

```
https://xxxxxxx.vercel.app/config/https://xxxxxxsubscribe?token=123456&file=https://github.com/Toperlock/sing-box-subscribe/raw/main/config_template/config_template_groups_rule_set_tun.json
```

```
https://xxxxxxx.vercel.app/config/https://xxxxxxsubscribe?token=123456&file=2
```

本地python执行脚本命令：

```
python main.py
```

或者你可以直接带template_index参数选定模板，0表示第一个模板(no flask不支持此参数)

```
python main.py --template_index=0
```

支持Docker

```
docker build --tag 'sing-box' .
docker run -p 5000:5000 sing-box:latest
```

支持自定义GitHub加速链接（使用参数&gh=1 数字代表使用第一个github加速），默认不加此参数。只有原始GitHub文件链接或者已经使用以下GitHub加速链接才能替换

```
1. "https://gh-proxy.com/",
2. "https://gh.sageer.me/",
3. "https://ghproxy.com/",
4. "https://mirror.ghproxy.com/",
5. "https://cdn.jsdelivr.net",
6. "https://testingcf.jsdelivr.net"
```


### 2026-02 Update (Multi Sources + URI + Safe Input)

The `/config` API has been extended:

- No 3-subscription limit anymore, supports any number of `source` entries
- Supports mixed input: normal subscription URLs + direct URI links (`vless://`, `vmess://`, `trojan://`, etc.)
- Keeps legacy format: `/config/<URL_OR_MULTI_URL>`
- Adds safer modes: `GET /config` and `POST /config` to avoid manual escaping of `|`, `#`, `&`

Recommended safe usage: `GET /config` with repeated `source`

```bash
curl -L --get --connect-timeout 10 --max-time 30 \
  --data-urlencode "source=https://prosto.pro1vpn.net/sub/REPLACE_ME" \
  --data-urlencode "source=vless://UUID@example.com:443?type=tcp&security=reality&pbk=PUBLIC_KEY&fp=chrome&sni=example.com&sid=SHORTID&spx=%2F&flow=xtls-rprx-vision#Proxy2" \
  --data-urlencode "file=https://raw.githubusercontent.com/Mendex777/sbshell_3/refs/heads/main/config_template/my/config_tproxy_25_07_2025_v1.json" \
  "http://localhost:5000/config" \
  -o /etc/sing-box/config.json
```

Optional: `POST /config` with JSON

```bash
curl -L --connect-timeout 10 --max-time 30 \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      "https://prosto.pro1vpn.net/sub/REPLACE_ME",
      "vless://UUID@example.com:443?type=tcp&security=reality&pbk=PUBLIC_KEY&fp=chrome&sni=example.com&sid=SHORTID&spx=%2F&flow=xtls-rprx-vision#Proxy2"
    ],
    "file": "https://raw.githubusercontent.com/Mendex777/sbshell_3/refs/heads/main/config_template/my/config_tproxy_25_07_2025_v1.json"
  }' \
  "http://localhost:5000/config" \
  -o /etc/sing-box/config.json
```

Legacy format (still supported):

```bash
curl -L --connect-timeout 10 --max-time 30 "http://localhost:5000/config/https://example-sub-1|https://example-sub-2&file=2" -o /etc/sing-box/config.json
```

### Custom Rule Sets from qx/surge/loon/clash Lists [https://github.com/Toperlock/sing-box-geosite](https://github.com/Toperlock/sing-box-geosite)

### wechat规则集源文件写法：
```json
{
  "version": 1,
  "rules": [
    {
      "domain": [
        "dl.wechat.com",
        "sgfindershort.wechat.com",
        "sgilinkshort.wechat.com",
        "sglong.wechat.com",
        "sgminorshort.wechat.com",
        "sgquic.wechat.com",
        "sgshort.wechat.com",
        "tencentmap.wechat.com.com",
        "qlogo.cn",
        "qpic.cn",
        "servicewechat.com",
        "tenpay.com",
        "wechat.com",
        "wechatlegal.net",
        "wechatpay.com",
        "weixin.com",
        "weixin.qq.com",
        "weixinbridge.com",
        "weixinsxy.com",
        "wxapp.tc.qq.com"
      ]
    },
    {
      "domain_suffix": [
        ".qlogo.cn",
        ".qpic.cn",
        ".servicewechat.com",
        ".tenpay.com",
        ".wechat.com",
        ".wechatlegal.net",
        ".wechatpay.com",
        ".weixin.com",
        ".weixin.qq.com",
        ".weixinbridge.com",
        ".weixinsxy.com",
        ".wxapp.tc.qq.com"
      ]
    },
    {
      "ip_cidr": [
        "101.32.104.4/32",
        "101.32.104.41/32",
        "101.32.104.56/32",
        "101.32.118.25/32",
        "101.32.133.16/32",
        "101.32.133.209/32",
        "101.32.133.53/32",
        "129.226.107.244/32",
        "129.226.3.47/32",
        "162.62.163.63/32"
      ]
    }
  ]
}
```
配置文件添加源文件规则集：
```
{
  "tag": "geosite-wechat",
  "type": "remote",
  "format": "source",
  "url": "https://raw.githubusercontent.com/Toperlock/sing-box-geosite/main/wechat.json",
  "download_detour": "auto"
}
```

