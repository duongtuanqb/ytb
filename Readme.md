## Install
- Create credentials:
```
https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials
```
- Download file credentials as name `credentials_file.json` and copy to source.

- Install library
```
$ pip install -r requirements.txt
```

## Use
- Login google
```
python main.py --login
```

- Like video
```
python main.py --rate like <id video>
```

- Subscript channel
```
python main.py --sub <id channel>
```