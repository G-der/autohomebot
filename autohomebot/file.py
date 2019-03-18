import time

class file():
    def Write(self, path, msg):

        try:
            f = open(path,'a+')
            strDateTime = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
            f.write('[' + strDateTime + '] ' + msg + '\n')
        except IOError:
            print("Error: 没有找到文件或读取文件失败")
        else:
            #print("内容写入文件成功")
            f.close()

    def ErrorWrite(self, msg):
        
        self.Write("error.log", msg)
    
    def InfoWrite(self, msg):
        
        self.Write("info.log", msg)