# ri_simulator

## Setup
```
$ ghq get -p git@github.com:ueki-kazuki/ri_simulator.git
$ pipenv shell
```

## Usage
```
$ env AWS_PROFILE=YOUR_AWS_PROFIE python app.py

=== RI covered instances ===
myserver001          t3.medium    Windows    i-0777b8a93bbafed66
=== RI *NOT* covered instances ===
myserver002          m3.medium    Linux/UNIX i-02840711223f51729
myserver003          t2.micro     Windows    i-0a4269eb765b01134  stopped
=== Purchased but not applied RI ===
                     t3.small     Windows    convertible    2 2021-12-04 01:31:37+00:00
```
