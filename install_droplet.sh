sudo apt upgrade -y
sudo apt-get install nginx -y
sudo service nginx start
sudo systemctl enable nginx

sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.10 -y
sudo apt install python3-pip -y