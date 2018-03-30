---
title: python 爬虫
---



# crawlers

>  crawlers in one `python 3.6`



## Thanks to

- [chenjiandongx](# https://github.com/chenjiandongx/awesome-spider)
- [爬虫攻防](https://www.zhuyingda.com/blog/article.html?id=17&origin=segment)
- [fuck-login](https://github.com/xchaoinfo/fuck-login)


## DONE

- [x] 静态图片下载
  - [44style](http://44.style/)
  - [mmjpg](www.mmjpg.com)
  - ...
- [x] google  crx 插件爬取
  - [chromecj](http://chromecj.com/)
  - [cnplugins](http://www.cnplugins.com)
- [x] luoo 网音乐
- [x] one 读书
- [x] [sdifen周](http://www.sdifen.com/)
- [x] [伯乐python资源](http://hao.jobbole.com/?catid=144)
- [x] 电影查询
      - [x] [电影天堂](http://www.dytt8.net/)
  - [x][66ys](http://66ys.cc/)
- [x] 东奥会计题库
- [x] 代理




## docker machines

### mongo

```sh
docker run --name luoo_mg \
  -v <YOU_BASE_DIR>/Luoo/db/data:/data/db \
  -p <YOU_PORT>:27017 \
  -d mongo:latest --smallfiles  
```

### redis

> 切记: 在启动前需要先建立好 data 目录, 和 redis.conf 文件

- docker

  ```sh
  docker run \
    --name=crawl_redis \
    -tid \
    -p <YOU_PORT>:6379 \
    -v <YOU_BASE_DIR>/Luoo/redis/data:/data \
    -v <YOU_BASE_DIR>/Luoo/redis/redis.conf:/usr/local/etc/redis/redis.conf \
    redis redis-server /usr/local/etc/redis/redis.conf
  ```



- `redis.conf`

  ```sh
  port 6379
  timeout 300
  loglevel verbose
  save 900 1
  save 300 10
  save 60 10000
  rdbcompression yes
  appendonly yes
  appendfsync everysec
  requirepass 123456
  ```


