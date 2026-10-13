修复首次申请 HTTPS 证书后目录切换导致 `geoip.dat` 路径错误、预设初始化中断和面板未启动的问题。
新增包含 ACME 安装目录切换、TLS 面板和 TLS Clash 订阅的回归测试。

基于本仓库已固定的 v3.6.0，首次部署自动创建 VLESS 直连与住宅两个节点、住宅 Socks5 出站、对应路由，并开启 Clash 订阅。

登录后台后，在 Xray 设置 → 出站填写住宅 Socks5 的地址、端口及认证信息，保存后导入 Clash/Mihomo 订阅使用。

预设只在首次部署时应用；重新安装和升级保留用户配置。住宅出站未配置或连接失败时，不自动回退到 VPS 出口。
面板版本、安装脚本和包内 Xray/规则文件固定。原 v3.6.0 教程版本及其安装包保持原样。

部署命令：
```bash
bash <(curl -fLsS https://raw.githubusercontent.com/kjxv/3x-ui/v3.6.0-preset.2/deploy/preset/install.sh)
```

安装包下载后由安装程序检查 checksums.txt；请允许实际入站端口以及面板和订阅端口通过云安全组。
完整说明见源码中的 deploy/preset/README.md。
