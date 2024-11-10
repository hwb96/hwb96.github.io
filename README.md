# 本地运行
```commandline
hugo server -D
```
# 创建新的文章
```commandline
hugo server -D
```
# 在新的电脑上克隆项目的两种方式

## 方式一克隆时直接包含子模块

```# 克隆主仓库和所有子模块
git clone --recursive https://github.com/hwb96/hwb96.github.io.git
```
## 方式二：先克隆主仓库，再更新子模块

```# 克隆主仓库
git clone https://github.com/hwb96/hwb96.github.io.git
```
# 初始化和更新子模块
```cd hwb96.github.io
git submodule init
git submodule update
```
子模块的更新：


```
# 更新子模块到最新版本
git submodule update --remote themes/hugo-kiera
```
查看子模块状态：


```# 查看子模块信息
git submodule status
```
记住：

子模块的内容不会自动随主仓库一起克隆，需要特别处理
子模块有自己的 Git 历史记录，可以独立管理
主仓库中记录的是子模块的特定提交版本（那个 5676dfa 就是提交的 hash）
更新子模块后，主仓库也需要提交这个更新

这就是为什么你在 GitHub 上看到 hugo-kiera @ 5676dfa 是一个链接，它指向的是主题仓库的特定版本。