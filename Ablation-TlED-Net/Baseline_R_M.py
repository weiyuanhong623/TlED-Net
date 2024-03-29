import torch
from torch import nn
from torchvision import models as resnet_model

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.conv(x)


class SingleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(SingleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.conv(x)

class MDFC_4(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(MDFC_4, self).__init__()

        self.brance_1=nn.Sequential(
            nn.Conv2d(in_channels,out_channels,3,1,1,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

        self.brance_2_2=nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 5, 1, 2, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


        self.brance_3=nn.Sequential(
            nn.Conv2d(in_channels,out_channels,7,1,3,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

        self.brance_4=nn.Conv2d(in_channels,in_channels,kernel_size=1)


        self.channels_tran_1=nn.Conv2d(2*in_channels,in_channels,kernel_size=1)     #256->128
        self.channels_tran_2=nn.Conv2d(4*in_channels,in_channels,kernel_size=1)    #512->128
        self.channels_tran_3=nn.Conv2d(in_channels,out_channels,kernel_size=1)    #128->256



        self.relu=nn.ReLU(inplace=True)

    def forward(self,x):
        b1=self.relu( x+self.channels_tran_1(self.brance_1(x)))         #1*
        b2=self.relu( x+self.channels_tran_2(torch.cat((self.brance_2_2(x),self.brance_2_2(x)),dim=1)))   #1*
        b3=self.relu( x+self.channels_tran_1(self.brance_3(x)))         #1*
        b4=self.brance_4(x)         #1*

        b_cat=self.relu( x+self.channels_tran_2(torch.cat((b1,b2,b3,b4),dim=1)))
        return self.channels_tran_3(b_cat)


class MDFC_3(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(MDFC_3, self).__init__()

        self.branch_1=nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


        self.branch_2=nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 5, 1, 2, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

        self.branch_3=nn.Conv2d(in_channels,in_channels,kernel_size=1)


        self.channel_tran_1=nn.Conv2d(2*in_channels,in_channels,kernel_size=1)
        self.channel_tran_2=nn.Conv2d(4*in_channels,in_channels,kernel_size=1)
        self.channel_tran_3=nn.Conv2d(3*in_channels,in_channels,kernel_size=1)
        self.channel_tran_4=nn.Conv2d(in_channels,out_channels,kernel_size=1)
        self.relu=nn.ReLU(inplace=True)


    def forward(self,x):
        b1=self.relu(x+self.channel_tran_1(self.branch_1(x)))       #1*
        b2=self.relu( x+self.channel_tran_2(torch.cat((self.branch_2(x),self.branch_2(x)),dim=1) )) #1*
        b3=self.branch_3(x)     #1*

        b_cat=self.relu( x+self.channel_tran_3(torch.cat((b1,b2,b3),dim=1)))

        return self.channel_tran_4(b_cat)


class Conv_1x1(nn.Module):
    def __init__(self,in_channels,out_channels):
        super(Conv_1x1, self).__init__()
        self.conv=nn.Sequential(
            nn.Conv2d(in_channels,out_channels,kernel_size=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self,x):
        return self.conv(x)


class Baseline_R_M(nn.Module):
    def __init__(self,in_channels,out_channels, features=[[64, 128, 256],
                                                          [128,256, 512],
                                                          [128,256,512]]):
        super(Baseline_R_M, self).__init__()
        self.downs_1 = nn.ModuleList()
        self.downs_2 = nn.ModuleList()
        self.downs_3 = nn.ModuleList()

        self.ups_1 = nn.ModuleList()
        self.ups_2 = nn.ModuleList()
        self.ups_3 = nn.ModuleList()

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.pool_2=nn.MaxPool2d(kernel_size=4,stride=4)
        self.pool_3=nn.MaxPool2d(kernel_size=8,stride=8)
        self.pool_4=nn.MaxPool2d(kernel_size=16,stride=16)

        resnet = resnet_model.resnet50(pretrained=True)

        self.firstconv = resnet.conv1
        self.firstbn = resnet.bn1
        self.firstrelu = resnet.relu
        self.encoder1 = resnet.layer1
        self.encoder2 = resnet.layer2
        self.encoder3 = resnet.layer3
        self.encoder4 = resnet.layer4
        self.conv1_1x1s=nn.ModuleList()
        self.trans_conv=nn.ConvTranspose2d(64,64,kernel_size=2,stride=2)
        self.relu=nn.ReLU(inplace=True)

        self.trans_conv_2=nn.ConvTranspose2d(128,64,kernel_size=2,stride=2)
        self.trans_conv_2_2=nn.ConvTranspose2d(128,64,kernel_size=2,stride=2)
        self.conv1_1x1_2=Conv_1x1(256,512)


        self.trans_conv_3=nn.ConvTranspose2d(1024,512,kernel_size=2,stride=2)
        self.trans_conv_4=nn.ConvTranspose2d(1024,256,kernel_size=4,stride=4)
        self.trans_conv_5=nn.ConvTranspose2d(1024,128,kernel_size=8,stride=8)
        self.trans_conv_6=nn.ConvTranspose2d(1024,64,kernel_size=16,stride=16)



        self.conv1_1x1s_2=nn.ModuleList()
        for i in [128,256,512]:
            self.conv1_1x1s_2.append(Conv_1x1(64,i))


        #resnet_channels_trans
        trans_channels=[128,256,512,1024]
        for trans_channel in trans_channels:
            self.conv1_1x1s.append(Conv_1x1(trans_channel*2,trans_channel))

        #Down part1 of demo
        for feature in features[0]:
            self.downs_1.append(DoubleConv(in_channels,feature))
            in_channels=feature

        self.downs_2.append(MDFC_4(128,256))
        self.downs_2.append(MDFC_3(256,512))

        #Down part3 of demo
        in_channels=128
        for feature in features[2][1:2]:
            self.downs_3.append(DoubleConv(in_channels, feature))
            in_channels = feature

        #Up part1 of demo
        for feature in reversed(features[2][:2]):
            self.ups_1.append(
                nn.ConvTranspose2d(
                    feature*2,feature,kernel_size=2,stride=2
                )
            )
            self.ups_1.append(DoubleConv(feature*3,feature))

        #Up part2 of demo
        for feature in reversed(features[1]):
            self.ups_2.append(
                nn.ConvTranspose2d(
                    feature*2,feature,kernel_size=2,stride=2
                )
            )
            self.ups_2.append(DoubleConv(feature * 3, feature))

        #Up part3 of demo
        for feature in reversed(features[0]):
            self.ups_3.append(
                nn.ConvTranspose2d(
                    feature*2,feature,kernel_size=2,stride=2
                )
            )
            if feature!=64:
                self.ups_3.append(SingleConv(feature * 5, feature))
            else:
                self.ups_3.append(SingleConv(feature * 6, feature))

        self.bottleneck1=DoubleConv(256*2,512)
        self.bottleneck2=DoubleConv(2*512,2*512)
        self.bottleneck3=DoubleConv(3*512,512)

        self.final_conv=nn.Conv2d(features[0][0],out_channels,kernel_size=1)



    def forward(self,x):
        skip_connections = []
        skip_connections_ex=[]
        skip_top=[]
        skip_bottleneck=[]


        #decoder ex_part
        e0=self.firstconv(x)
        e0=self.firstbn(e0)
        e0=self.firstrelu(e0)
                 #64,256,256
        skip_connections_ex.append(self.trans_conv(e0))     #64,512,512



        e1=self.encoder1(e0)
                 #256,256,256->128,256,256
        skip_connections_ex.append((self.conv1_1x1s[0](e1)))
        e2=self.encoder2(e1)
                 #512,128,128->256,128,128
        skip_connections_ex.append((self.conv1_1x1s[1](e2)))
        e3=self.encoder3(e2)
                 #1024,64,64->512,64,64
        skip_connections_ex.append((self.conv1_1x1s[2](e3)))
        e4=self.encoder4(e3)
                  #2048,32,32->1024,32,32
        skip_connections_ex.append((self.conv1_1x1s[3](e4)))


        #encoder part1
        for i in range(len(self.downs_1)):
            x=self.downs_1[i](x)
            skip_connections.append(x)
            x=self.pool(x)

        x=self.bottleneck1(torch.cat((self.pool(skip_connections_ex[2]),x),dim=1))           #512
        skip_bottleneck.append(x)

        #decoder part1
        index_de_1=1
        for idx in range(0,len(self.ups_1),2):
            x=self.ups_1[idx](x)
            concat_skip=torch.cat((skip_connections_ex[::-1][idx//2+2],skip_connections[::-1][idx//2],x),dim=1)

            index_de_1-=1
            x=self.ups_1[idx+1](concat_skip)

        skip_connections.append(x)

        # encoder part2
        x2 = self.pool(x)
        x2 = self.downs_2[0](x2)
        skip_connections.append(x2)

        x2 = self.pool(x2)
        x2 = self.downs_2[1](x2)
        skip_connections.append(x2)
        x2=self.pool(x2)
        x2=self.bottleneck2(torch.cat((self.pool(skip_bottleneck[0]),x2),dim=1))
        x2=self.relu(x2+skip_connections_ex[4])

        skip_bottleneck.append(self.trans_conv_3(x2))       #512        64
        skip_bottleneck.append(self.trans_conv_4(x2))       #256        128
        skip_bottleneck.append(self.trans_conv_5(x2))       #128        256
        skip_bottleneck.append(self.trans_conv_6(x2))       #64         512

        #decoder part2
        index_de_2=2
        for idx in range(0,len(self.ups_2),2):
            x2=self.ups_2[idx](x2)

            if idx==0:
                concat_skip=torch.cat((skip_connections_ex[3],skip_connections[::-1][idx//2],x2),dim=1)
            else:
                concat_skip=torch.cat((skip_connections_ex[::-1][idx//2+1],skip_connections[::-1][idx // 2],x2),dim=1)
            index_de_2-=1
            x2=self.ups_2[idx+1](concat_skip)

        x=x+x2
        skip_connections.append(x)

        #encoder part3
        for down in self.downs_3:   #256
            x=self.pool(x)
            x=down(x)
            skip_connections.append(x)
        x=self.pool(x)
        x=self.conv1_1x1_2(x)
        x=self.bottleneck3(torch.cat((skip_bottleneck[1],skip_connections_ex[3],x),dim=1))


        for index in range(3,7,3):
            skip_top.append(self.trans_conv_2(skip_connections[index]))

        #decoder part3
        index_de_3=1
        for idx in range(0,len(self.ups_3),2):
            x=self.ups_3[idx](x)

            if idx==0:
                concat_skip=torch.cat((skip_bottleneck[2],skip_connections_ex[2],skip_connections[::-1][idx//2+5],skip_connections[::-1][idx // 2],x),dim=1)
            elif idx==2:
                concat_skip=torch.cat((skip_bottleneck[3],skip_connections_ex[1],skip_connections[::-1][idx//2+5],skip_connections[::-1][idx // 2],x),dim=1)
            else:
                concat_skip=torch.cat((skip_bottleneck[4],skip_top[1],skip_top[0],skip_connections_ex[0],skip_connections[0],x),dim=1)

            index_de_3-=1
            x=self.ups_3[idx+1](concat_skip)

        return self.final_conv(x)
