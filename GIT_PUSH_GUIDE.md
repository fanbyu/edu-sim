# Git 推送指南

## 📋 当前状态

✅ **本地提交已完成**  
⏳ **等待推送到 GitHub**

---

## 🔍 问题诊断

当前遇到的网络问题：
- HTTPS 连接被重置 (`Connection was reset`)
- 无法连接到 github.com:443

这通常是由于：
1. 网络防火墙限制
2. 需要配置代理
3. GitHub 访问不稳定

---

## ✅ 解决方案

### 方案 1: 稍后重试（推荐）

网络可能是暂时性问题，稍后再试：

```bash
git push origin main
```

---

### 方案 2: 使用代理（如果你有）

如果你有 HTTP/HTTPS 代理：

```bash
# 配置 Git 使用代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 推送
git push origin main

# 推送完成后可以取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

**常见代理端口:**
- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809`
- Shadowsocks: `http://127.0.0.1:1080`

---

### 方案 3: 使用 SSH（需要配置 SSH Key）

#### 步骤 1: 生成 SSH Key（如果还没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### 步骤 2: 添加 SSH Key 到 GitHub

1. 复制公钥：
   ```bash
   cat $env:USERPROFILE\.ssh\id_ed25519.pub
   ```

2. 访问 https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥并保存

#### 步骤 3: 切换远程 URL 为 SSH

```bash
git remote set-url origin git@github.com:fanbyu/edu-sim.git
```

#### 步骤 4: 测试连接

```bash
ssh -T git@github.com
# 应该看到: Hi fanbyu! You've successfully authenticated...
```

#### 步骤 5: 推送

```bash
git push origin main
```

---

### 方案 4: 使用 GitHub Desktop

如果命令行推送困难，可以使用图形化工具：

1. 下载 [GitHub Desktop](https://desktop.github.com/)
2. 克隆仓库或添加现有仓库
3. 同步更改

---

## 📊 待推送的内容

### 最新提交

```
commit 1162954 (HEAD -> main)
docs: Update README to Chinese (Edu-Sim v0.3.0)

- Complete Chinese documentation
- Added quick start guide with LLM provider configuration
- Detailed core features and CLI commands
- System architecture diagram
- Visualization features
- Typical workflows and use cases
- Comparison with original MiroFish
- Comprehensive documentation links
```

### 文件变更统计

- **README.md**: +422 行, -119 行（完全中文化）

---

## 🎯 推送后的验证

推送成功后，检查以下内容：

### 1. 验证远程提交

```bash
git log origin/main --oneline -3
```

应该看到：
```
1162954 docs: Update README to Chinese (Edu-Sim v0.3.0)
6921def feat: Add universal LLM provider support
6fcf6fa feat: Complete Edu-Sim refactoring with Graphify integration
```

### 2. 访问 GitHub 仓库

打开浏览器访问：
https://github.com/fanbyu/edu-sim

确认：
- ✅ README 显示为中文
- ✅ 最新版本号 v0.3.0
- ✅ 所有文件都已更新

---

## 💡 预防措施

### 配置 Git 自动重试

```bash
# 增加超时时间
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 增加缓冲区
git config --global http.postBuffer 524288000
```

### 使用 Git LFS（如果有很多大文件）

```bash
git lfs install
git lfs track "*.pdf"
git lfs track "*.zip"
```

---

## 📞 需要帮助？

如果以上方法都不行：

1. **检查网络状态**
   ```bash
   ping github.com
   curl -I https://github.com
   ```

2. **查看 Git 详细日志**
   ```bash
   GIT_CURL_VERBOSE=1 GIT_TRACE=1 git push origin main
   ```

3. **尝试其他网络**
   - 切换到手机热点
   - 使用不同的 WiFi

4. **联系网络管理员**
   - 确认是否阻止了 GitHub 访问
   - 请求开放 443 端口

---

## ✨ 总结

**当前状态:**
- ✅ 所有代码已本地提交
- ⏳ 等待网络稳定后推送

**下一步:**
1. 检查网络连接
2. 选择上述方案之一
3. 运行 `git push origin main`
4. 验证推送成功

**预计推送内容:**
- 1 个提交
- README.md 完全中文化
- 约 422 行新增内容

---

**最后更新**: 2026-04-07  
**分支**: main  
**待推送提交**: 1 个
