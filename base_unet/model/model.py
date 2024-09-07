import torch
import torch.nn as nn


class Unet(nn.Module):
    def __init__(self, num_classes):
        super(Unet, self).__init__()
        self.stage_1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )

        self.stage_2 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
        )

        self.stage_3 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
        )

        self.stage_4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
        )

        self.stage_5 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=3, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(),
            nn.Conv2d(in_channels=1024, out_channels=1024, kernel_size=3, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(),
        )

        self.upsample_4 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=1024, out_channels=512, kernel_size=4, stride=2, padding=1)
        )
        self.upsample_3 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=512, out_channels=256, kernel_size=4, stride=2, padding=1)
        )
        self.upsample_2 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=4, stride=2, padding=1)
        )
        self.upsample_1 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=4, stride=2, padding=1)
        )

        self.stage_up_4 = nn.Sequential(
            nn.Conv2d(in_channels=1024, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU()
        )

        self.stage_up_3 = nn.Sequential(
            nn.Conv2d(in_channels=512, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU()
        )

        self.stage_up_2 = nn.Sequential(
            nn.Conv2d(in_channels=256, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        self.stage_up_1 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )

        self.final = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=num_classes, kernel_size=3, padding=1),
        )

    def forward(self, x):
        x = x.float()
        # 下采样过程
        stage_1 = self.stage_1(x)
        stage_2 = self.stage_2(stage_1)
        stage_3 = self.stage_3(stage_2)
        stage_4 = self.stage_4(stage_3)
        stage_5 = self.stage_5(stage_4)

        # 1024->512
        up_4 = self.upsample_4(stage_5)
        # 512+512 -> 512\

        up_4_conv = self.stage_up_4(torch.cat([up_4, stage_4], dim=1))

        # 512 -> 256
        up_3 = self.upsample_3(up_4_conv)
        # 256+256 -> 256
        up_3_conv = self.stage_up_3(torch.cat([up_3, stage_3], dim=1))

        up_2 = self.upsample_2(up_3_conv)
        up_2_conv = self.stage_up_2(torch.cat([up_2, stage_2], dim=1))

        up_1 = self.upsample_1(up_2_conv)
        up_1_conv = self.stage_up_1(torch.cat([up_1, stage_1], dim=1))

        output = self.final(up_1_conv)

        return output


class ContinusParalleConv(nn.Module):
    # 一个连续的卷积模块，包含BatchNorm 在前 和 在后 两种模式
    def __init__(self, in_channels, out_channels, pre_Batch_Norm=True):
        super(ContinusParalleConv, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels

        if pre_Batch_Norm:
            self.Conv_forward = nn.Sequential(
                nn.BatchNorm2d(self.in_channels),
                nn.ReLU(),
                nn.Conv2d(self.in_channels, self.out_channels, 3, padding=1),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(),
                nn.Conv2d(self.out_channels, self.out_channels, 3, padding=1))

        else:
            self.Conv_forward = nn.Sequential(
                nn.Conv2d(self.in_channels, self.out_channels, 3, padding=1),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(),
                nn.Conv2d(self.out_channels, self.out_channels, 3, padding=1),
                nn.BatchNorm2d(self.out_channels),
                nn.ReLU())

    def forward(self, x):
        x = self.Conv_forward(x)
        return x


class UnetPlusPlus(nn.Module):
    def __init__(self, num_classes, deep_supervision=False):
        super(UnetPlusPlus, self).__init__()
        self.num_classes = num_classes
        self.deep_supervision = deep_supervision
        self.filters = [64, 128, 256, 512, 1024]

        self.CONV3_1 = ContinusParalleConv(512 * 2, 512, pre_Batch_Norm=True)

        self.CONV2_2 = ContinusParalleConv(256 * 3, 256, pre_Batch_Norm=True)
        self.CONV2_1 = ContinusParalleConv(256 * 2, 256, pre_Batch_Norm=True)

        self.CONV1_1 = ContinusParalleConv(128 * 2, 128, pre_Batch_Norm=True)
        self.CONV1_2 = ContinusParalleConv(128 * 3, 128, pre_Batch_Norm=True)
        self.CONV1_3 = ContinusParalleConv(128 * 4, 128, pre_Batch_Norm=True)

        self.CONV0_1 = ContinusParalleConv(64 * 2, 64, pre_Batch_Norm=True)
        self.CONV0_2 = ContinusParalleConv(64 * 3, 64, pre_Batch_Norm=True)
        self.CONV0_3 = ContinusParalleConv(64 * 4, 64, pre_Batch_Norm=True)
        self.CONV0_4 = ContinusParalleConv(64 * 5, 64, pre_Batch_Norm=True)

        self.stage_0 = ContinusParalleConv(3, 64, pre_Batch_Norm=False)
        self.stage_1 = ContinusParalleConv(64, 128, pre_Batch_Norm=False)
        self.stage_2 = ContinusParalleConv(128, 256, pre_Batch_Norm=False)
        self.stage_3 = ContinusParalleConv(256, 512, pre_Batch_Norm=False)
        self.stage_4 = ContinusParalleConv(512, 1024, pre_Batch_Norm=False)

        self.pool = nn.MaxPool2d(2)

        self.upsample_3_1 = nn.ConvTranspose2d(in_channels=1024, out_channels=512, kernel_size=4, stride=2, padding=1)

        self.upsample_2_1 = nn.ConvTranspose2d(in_channels=512, out_channels=256, kernel_size=4, stride=2, padding=1)
        self.upsample_2_2 = nn.ConvTranspose2d(in_channels=512, out_channels=256, kernel_size=4, stride=2, padding=1)

        self.upsample_1_1 = nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=4, stride=2, padding=1)
        self.upsample_1_2 = nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=4, stride=2, padding=1)
        self.upsample_1_3 = nn.ConvTranspose2d(in_channels=256, out_channels=128, kernel_size=4, stride=2, padding=1)

        self.upsample_0_1 = nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=4, stride=2, padding=1)
        self.upsample_0_2 = nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=4, stride=2, padding=1)
        self.upsample_0_3 = nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=4, stride=2, padding=1)
        self.upsample_0_4 = nn.ConvTranspose2d(in_channels=128, out_channels=64, kernel_size=4, stride=2, padding=1)

        # 分割头
        self.final_super_0_1 = nn.Sequential(
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, self.num_classes, 3, padding=1),
        )
        self.final_super_0_2 = nn.Sequential(
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, self.num_classes, 3, padding=1),
        )
        self.final_super_0_3 = nn.Sequential(
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, self.num_classes, 3, padding=1),
        )
        self.final_super_0_4 = nn.Sequential(
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, self.num_classes, 3, padding=1),
        )

    def forward(self, x):
        x_0_0 = self.stage_0(x)
        x_1_0 = self.stage_1(self.pool(x_0_0))
        x_2_0 = self.stage_2(self.pool(x_1_0))
        x_3_0 = self.stage_3(self.pool(x_2_0))
        x_4_0 = self.stage_4(self.pool(x_3_0))

        x_0_1 = torch.cat([self.upsample_0_1(x_1_0), x_0_0], 1)
        x_0_1 = self.CONV0_1(x_0_1)

        x_1_1 = torch.cat([self.upsample_1_1(x_2_0), x_1_0], 1)
        x_1_1 = self.CONV1_1(x_1_1)

        x_2_1 = torch.cat([self.upsample_2_1(x_3_0), x_2_0], 1)
        x_2_1 = self.CONV2_1(x_2_1)

        x_3_1 = torch.cat([self.upsample_3_1(x_4_0), x_3_0], 1)
        x_3_1 = self.CONV3_1(x_3_1)

        x_2_2 = torch.cat([self.upsample_2_2(x_3_1), x_2_0, x_2_1], 1)
        x_2_2 = self.CONV2_2(x_2_2)

        x_1_2 = torch.cat([self.upsample_1_2(x_2_1), x_1_0, x_1_1], 1)
        x_1_2 = self.CONV1_2(x_1_2)

        x_1_3 = torch.cat([self.upsample_1_3(x_2_2), x_1_0, x_1_1, x_1_2], 1)
        x_1_3 = self.CONV1_3(x_1_3)

        x_0_2 = torch.cat([self.upsample_0_2(x_1_1), x_0_0, x_0_1], 1)
        x_0_2 = self.CONV0_2(x_0_2)

        x_0_3 = torch.cat([self.upsample_0_3(x_1_2), x_0_0, x_0_1, x_0_2], 1)
        x_0_3 = self.CONV0_3(x_0_3)

        x_0_4 = torch.cat([self.upsample_0_4(x_1_3), x_0_0, x_0_1, x_0_2, x_0_3], 1)
        x_0_4 = self.CONV0_4(x_0_4)

        if self.deep_supervision:
            out_put1 = self.final_super_0_1(x_0_1)
            out_put2 = self.final_super_0_2(x_0_2)
            out_put3 = self.final_super_0_3(x_0_3)
            out_put4 = self.final_super_0_4(x_0_4)
            return [out_put1, out_put2, out_put3, out_put4]
        else:
            return self.final_super_0_4(x_0_4)