Prepare_smp_command = [
    '-os 10=[0:0:1:0:0:1]',
    '-os 70=[1:1:1:0]',
    '-os 43=[1:1:0:0:1:2:3:4:5:6]',
    [f"-os {_}=[0:0:0:0:0:0:0:0:0:0]" for _ in range(44, 67)],
    [f"-os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(11, 43)],
    [f"-os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(68, 69)],
    '-os 67=[1:1:7:6:1:7:11:1:7:16:1:7:21:1:7:26:1:7:1:2:7:6:2:7:11:2:7:16:2:7:21:2:7:26:2:7:1:3:7:6:3:7:11:3'
    ':7:16:3:7]',
    [f"-os {_}=[0:1:2:3:4:5:6:7:8:9:10:11:12:13:14:15:16:17:18:19:20:21:22:23:24:25:26:27:28:29:30:31:32:33:34"
     f":35:36:37:38:39:40:41:42:43:44:45:46:47]" for _ in range(11, 18)]
]
