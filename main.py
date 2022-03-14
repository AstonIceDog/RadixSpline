import pandas as pd
import time


# 预测位置
def predict(x, left_key, right_key, left_position, right_position):
    result = left_position + (x - left_key) * (right_position - left_position) / (right_key - left_key)
    return result


# 键值对 坐标表示 x键 y位置
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# 构建通道
def greedy_spline_corridor(s, n, e):
    r = []                                  # 存放结果
    b = s[0]                                # 将第0个设为基点
    r.append(b)
    u = Coordinate(s[1].x, s[1].y + e)      # 上限
    l = Coordinate(s[1].x, s[1].y - e)      # 下限
    for i in range(2, n):
        c = s[i]
        k_bc = (c.y - b.y) / (c.x - b.x)
        k_bu = (u.y - b.y) / (u.x - b.x)
        k_bl = (l.y - b.y) / (l.x - b.x)
        if k_bc > k_bu or k_bc < k_bl:      # 如果bc在bu左边或bl右边，即bc斜率大于bu或小于bl,即c点不在通道内
            b = s[i - 1]                    # 将前一个设为基点
            r.append(b)
            u.y = c.y + e
            u.x = c.x
            l.y = c.y - e
            l.x = c.x                       # 更新上下限
        else:                               # 否则在通道内
            u_prime = Coordinate(c.x, c.y + e)
            l_prime = Coordinate(c.x, c.y - e)
            k_bu = (u.y - b.y) / (u.x - b.x)
            k_bl = (l.y - b.y) / (l.x - b.x)
            k_bu_prime = (u_prime.y - b.y) / (u_prime.x - b.x)
            k_bl_prime = (l_prime.y - b.y) / (l_prime.x - b.x)
            if k_bu > k_bu_prime:
                u = u_prime
            if k_bl < k_bl_prime:
                l = l_prime
    r.append(s[n - 1])
    return r


# R = greedy_spline_corridor(data, data_count, E)
# knot_count = len(R)
# r = 18          # 前缀大小


# 构建基表
def build_radix_table(array, n, r):
    radix_table = {}
    # 第一个
    # bi_data = bin(array[0])[2:]
    bi_data = '{:064b}'.format(array[0].x)      # 转换为32位2进制
    # print(bi_data)
    predix = bi_data[:r]                        # 选取r位前缀
    predix = int(predix, 2)                     # 将二进制字符串转换为整数
    # print(predix)
    pre_predix = predix
    radix_table[predix] = 0                     # 将前缀对应的数的下标保存下来
    # 从第二个开始
    for i in range(1, n):
        # bi_data = bin(array[i])[2:]
        bi_data = '{:064b}'.format(array[i].x)  # 转换为2进制
        predix = bi_data[:r]                    # 选取r位前缀
        predix = int(predix, 2)                 # 将二进制字符串转换为整数
        if predix != pre_predix:                # 如果前缀不同
            pre_predix = predix
            radix_table[predix] = i             # 将前缀对应的数在样条点表中的下标保存下来
    return radix_table


# print(build_radix_table(R, knot_count, r))

def bin_search(data_list, val):
    low = 0                                     # 最小数下标
    high = len(data_list) - 1                   # 最大数下标
    while low <= high:
        mid = (low + high) // 2                 # 中间数下标
        if data_list[mid].x == val:             # 如果中间数下标等于val, 返回
            return mid
        elif data_list[mid].x > val:            # 如果val在中间数左边, 移动high下标
            high = mid - 1
        else:                                   # 如果val在中间数右边, 移动low下标
            low = mid + 1
    return                                      # val不存在, 返回None


# 返回 x 在 arr 中的索引，如果不存在返回 -1
def binary_search(arr, l, r, x):
    # 基本判断
    if r >= l:
        mid = int(l + (r - l) / 2)
        # 元素整好的中间位置
        if arr[mid].x == x:
            return mid
            # 元素小于中间位置的元素，只需要再比较左边的元素
        elif arr[mid].x > x:
            return binary_search(arr, l, mid - 1, x)
            # 元素大于中间位置的元素，只需要再比较右边的元素
        else:
            return binary_search(arr, mid + 1, r, x)
    else:
        # 不存在
        return -1


# 查找位置(查找数据x,基表radix_table,前缀大小r,原数据data,误差e,样条表spline_array)
def lookup(x, radix_table, r, data, e, spline_array):
    bi_data = '{:064b}'.format(x)               # 转换为64位二进制数
    predix = bi_data[:r]                    # 取r位前缀
    predix = int(predix, 2)  # 将二进制字符串转换为整数
    radix_table_keys = list(radix_table.keys())
    # print(radix_table_keys)
    # length = len(radix_table.keys())
    # b = -1
    # for i in range(length - 1):                 # 根据前缀b找到b和b+1
    #     if radix_table_keys[i] == predix:       # 正好找到前缀，则保存b和b+1
    #         b = radix_table_keys[i]
    #         post_b = radix_table_keys[i + 1]
    #     elif radix_table_keys[i] > predix:      # 找到大于前缀的key，保存b-1和b+1
    #         pre_b = radix_table_keys[i - 1]
    #         post_b = radix_table_keys[i]
    # # 保存两个基数的位置
    # if b != -1:
    #     left = radix_table[b]
    #     right = radix_table[post_b]
    # elif b == -1:
    #     left = radix_table[pre_b]
    #     right = radix_table[post_b]
    # radix_table.keys()
    # 在样条表中查找到两个样条点
    length = len(spline_array)
    for i in range(length):
        pre_spline = Coordinate(spline_array[i - 1].x, spline_array[i - 1].y)
        post_spline = Coordinate(spline_array[i].x, spline_array[i].y)
        if spline_array[i].x >= x:
            pre_spline = Coordinate(spline_array[i - 1].x, spline_array[i - 1].y)
            post_spline = Coordinate(spline_array[i].x, spline_array[i].y)
            break

    # 然后使用线性插值预测位置
    predict_position = int(predict(x, pre_spline.x, post_spline.x, pre_spline.y, post_spline.y))
    # print(predict_position)
    # for i in range(predict_position - e, predict_position + e):
    #     if data[i] == x:
    #         return data[i]          # 返回键值对
    # for key in radix_table.keys():
    #     if key >= predix:
    #         b = key
    # position = bin_search(data[predict_position - e: predict_position + e], x)
    # return position
    # 最后使用二分查找在误差范围内查找位置
    left = predict_position - e
    right = predict_position + e
    if left < 0:
        left = 0
    if right > len(data):
        right = len(data)

    position = binary_search(data, left, right, x)
    return predict_position, position


e = 2  # epsilon 误差大小
r = 40  # 前缀大小

data = []
data_count = 0  # 元素个数

in_filename = 'amazon_com_1.csv'
dataset = pd.read_csv(in_filename)
# dataset = dataset[]

keys = dataset.key
positions = dataset.position
# print(keys[0])
# print(type(keys[0]))
for key, position in zip(keys, positions):
    # print(key)
    # print(position)
    data.append(Coordinate(key, position))
    data_count = data_count + 1
spline_array = greedy_spline_corridor(data, data_count, e)
knot_count = len(spline_array)
# print(knot_count)
radix_table = build_radix_table(spline_array, knot_count, r)
# print(radix_table.keys())
# print(radix_table)
# print(len(radix_table))
# print(spline_array[0].y)
# 1409531090,14112
sum_delta = 0
max_delta = 0
min_delta = 10000
delta_time = 0
time_start = time.time()
for key in keys:
    predict_position, position = lookup(key, radix_table, r, data, e, spline_array)
    delta = abs(predict_position - position)
    sum_delta += delta
    # print(delta_position)
    if delta > max_delta:
        max_delta = delta
    if delta < min_delta:
        min_delta = delta
time_end = time.time()
delta_time = time_end - time_start

avg_delta = sum_delta / data_count
print("最大误差：" + str(max_delta))
print("最小误差：" + str(min_delta))
print("平均误差：" + str(avg_delta))
print("查找用时：" + str(delta_time))

# 22~34位
# print(bin(9993697079))
# print(bin(2247399))
# print(data)
# print(data_count)
