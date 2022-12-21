起動方法
- カレントディレクトリにlogsがある場合
```sh
docker run -it --rm -p 6006:6006 -v $PWD/logs:/logs tensorboard  
```