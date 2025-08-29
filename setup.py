import os

print("""[0] pip\n[1] pip3\nWhich one do you use?""")

c = input(">>>: ")
if c == "0":
    os.system("apt-get install python")
    os.system("apt-get install python2")
    os.system("apt-get install python3")
    os.system("pip install cloudscraper")
    os.system("pip install socks")
    os.system("pip install pysocks")
    os.system("pip install colorama")
    os.system("pip install httpx")

elif c == "1":
    os.system("apt-get install python")
    os.system("apt-get install python2")
    os.system("apt-get install python3")
    os.system("pip3 install cloudscraper")
    os.system("pip3 install socks")
    os.system("pip3 install pysocks")
    os.system("pip3 install colorama")
    os.system("pip3 install httpx")
   
print("Done.")
