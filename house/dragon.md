## python 模拟微信登陆

### 1. 参考

[PC上对限制在微信客户端访问的html页面进行调试](https://www.cnblogs.com/meitian/p/5424587.html)
[移动应用抓包调试利器Charles](https://www.jianshu.com/p/68684780c1b0)
[使用Charles抓包模拟微信登录](https://www.jianshu.com/p/beaa56846f50)
[微信公众平台开发——微信授权登录（OAuth2.0）](https://www.cnblogs.com/0201zcr/p/5131602.html)

### 2. 操作步骤

- 电脑开启charles
- 手机连接wifi, 与电脑处于同一网络, 指向电脑代理
- 手机登陆成功
- 在电脑上面将登陆成功的cookies信息复制到文件`cks.txt`
- 设置待抓取房源值列表 [`1,2,3,4,5`]
- 启动程序

### 3. cookies 方式

- [ ] 如何获取cookies
- [ ] 如何将获取的cookies传入程序

#### 3.1 cookie样例

```python
cks = {
	"aliyungf_tc": "AQAAAF2ZBE1s2wIAorjHbzlAxKRMhrcq",
	"PHPSESSID": "cblela9d3lnadc6vldpjlnt365",
	"env_orgcode": "lkycadmin",
	"public_no_token": "...",
	"yunke_org_id": "...",
	"ztc_org_id": "...",
	"last_env": "g2"
}

# changed 
PHPSESSID = "cblela9d3lnadc6vldpjlnt365"
```

#### 3.2 如何获取 cookies

- 电脑开启charles
- 手机连接wifi, 与电脑处于同一网络, 指向电脑代理
- 手机登陆成功
- 在电脑上面将登陆成功的cookies信息复制到文件`cookies.txt`

#### 3.3 cookies传入程序

- 可以用笔记本专门用来抓包, 电脑登陆微信
- 复制charles cookies信息发给其他运行程序电脑
- 放置于程序运行目录

### 4. url 分析

#### 4.1 `post login`

```js
method: post
url: https://ztcwx.myscrm.cn/index.php?r=choose-room-activity/confirm-login
form: token=plyhue1441694274&activityId=3421&mobile=13207147931&idCardNo=421125199204241715
response = {
	"retCode": "0",
	"retMsg": "",
	"data": true
}
```

