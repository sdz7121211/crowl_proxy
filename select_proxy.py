#-*- encoding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding("utf-8")


def select(f):
    out = open("out.txt", "a")
    for line in f.readlines():
        temp = line.split(":")
        port = []
        print temp[1]
        for item in temp[1][0:]:
            print "item", item
            if item.isdigit():
                port.append(item)
            else:
                break
        port = "".join(port)
        print "port", port
        result = "".join([temp[0], ":", port, "\n"])
        out.write(result)


def main():
    f = open("ip_proxy.db", "rU")
    select(f)

if __name__ == "__main__":
    main()
