# coding: UTF-8

from PIL import ImageFont,Image,ImageDraw

def min_element(table_d,ignoring_index = None):
	min_i,min_j,min_e = 0,0,max(table_d.values())
	for key in table_d.keys():

		# ignore if i in key or j in key
		if ignoring_index is not None:
			i,j = key
			if i in ignoring_index or j in ignoring_index:
				continue

		if min_e > table_d[key]:
			min_e = table_d[key]
			min_i ,min_j = key

	return (min_i,min_j,min_e)

def to_dict(table):
	table_d = dict()
	for i in range(len(table)):
		for j in range(i):
			table_d[(i,j)] = table[i][j]
			table_d[(j,i)] = table[i][j]
	return table_d


def next_key(d,original_length,ignoring_keys=[],attension_values=[]):
	if len(ignoring_keys) == 0:
		return min(d.keys())
	save_key = None
	for k in d.keys():
		v_1,v_2 = d[k]
		if k in ignoring_keys:
			continue
		if not ((v_1 in ignoring_keys or v_1 < original_length) and (v_2 in ignoring_keys or v_2 < original_length)):
			continue

		if save_key is None:
			save_key = k
		if v_1 in attension_values or v_2 in attension_values:
			return k
	return save_key



def main():
	# in "sample" file
	#
	# 0 0.1 0.12 0.21
	# 0.1 0 0.04 0.13
	# 0.12 0.04 0 0.11
	# 0.21 0.13 0.11 0

	with open("sample","r") as f:
		lines = f.readlines()

	table = []
	for l in lines:
		row = [float(i) for i in l.split(" ")]
		table.append(row)

	table_d = to_dict(table)

	num_of_element = len(table)

	cluster = dict()
	cluster_num = dict()
	ignoring_index = []
	original_length = len(table)

	while True:


		# ignoring_index内にないもののなかで最小のものを選ぶ
		min_i,min_j,_ = min_element(table_d,ignoring_index)

		# 以降無視
		ignoring_index.append(min_i)
		ignoring_index.append(min_j)

		new_cluster = num_of_element # i&j を新しい要素とする

		cluster[new_cluster] = (min_i,min_j)
		cluster_num[new_cluster] = 0

		cluster_elements = 2
		if min_i in cluster_num.keys():
			cluster_num[new_cluster] += cluster_num[min_i]
			cluster_elements -= 1
		if min_j in cluster_num.keys():
			cluster_num[new_cluster] += cluster_num[min_j]
			cluster_elements -= 1
		cluster_num[new_cluster] += cluster_elements

		print(cluster_num)
		if max(cluster_num.values()) == original_length:
			print(cluster)
			print(cluster_num)
			print(table_d)
			print("UPGMA is end")
			break



		# clusterが所有するオリジナルの要素数
		weight_i = 1
		weight_j = 1
		if min_i in cluster_num.keys():
			weight_i = cluster_num[min_i]
		if min_j in cluster_num.keys():
			weight_j = cluster_num[min_j]

		for itr in range(num_of_element):
			if itr in ignoring_index:
				continue
			# テーブルの更新
			table_d[(itr,new_cluster)] = (table_d[(itr,min_i)]*weight_i + table_d[(itr,min_j)]*weight_j) / float(weight_i + weight_j)
			table_d[(new_cluster,itr)] = (table_d[(itr,min_i)]*weight_i + table_d[(itr,min_j)]*weight_j) / float(weight_i + weight_j)

		num_of_element += 1
		if len(ignoring_index) - num_of_element == 1:
			# Once the remaining elements are two, the distance is obvious.
			break

	# イメージの操作
	# ref: https://ailog.site/2020/03/09/0309/


	# 以降は系統樹の作成
	# 元々白紙が用意されているものとする
	img = Image.open('base.png')

	width,height = img.size
	draw = ImageDraw.Draw(img)

	# padding
	top_padding = int(height*0.01)
	bottom_padding = int(height*0.01)
	right_padding = int(width*0.01)
	left_padding = int(width*0.01)

	# ラベルに使う領域の高さ
	label_height = 64
	# 系統樹に使う高さ
	main_frame_height = height - top_padding - bottom_padding - label_height
	# 高さと系統樹の高さをそろえるための倍率
	height_scaler = main_frame_height / float(max(table_d.values()) / 2 )
	# ラベル間の幅
	interval = int((width - right_padding - left_padding) / (original_length+1))



	font = ImageFont.truetype("arial.ttf", 32) # font size is 64

	ignoring_keys = []
	attension_values = []
	painted_number = 0
	cluster_x = dict()
	cluster_y = dict()
	cluster_stack = dict()

	for i in range(original_length):
		cluster_y[i] = top_padding + main_frame_height
		cluster_stack[i] = 0.

	while True:
		key = next_key(cluster,original_length,ignoring_keys,attension_values)

		if key in attension_values:
			attension_values.remove(key)
		if key is None:
			break


		i,j = cluster[key]

		if not i in cluster_x.keys():
			cluster_x[i] = left_padding + interval * (painted_number + 1)
			painted_number += 1
		if not j in cluster_x.keys():
			cluster_x[j] = left_padding + interval * (painted_number + 1)
			painted_number += 1
		cluster_x[key] = int((cluster_x[i] + cluster_x[j]) / 2)
		edge_height = int((table_d[(i,j)] * height_scaler / 2))
		cluster_y[key] = top_padding + main_frame_height - edge_height

		if not key in cluster_stack.keys():
			cluster_stack[key] = table_d[(i,j)] / 2

		draw.line((cluster_x[i], cluster_y[i], cluster_x[i], cluster_y[key]), fill=(0, 0, 0), width=10)
		draw.line((cluster_x[j], cluster_y[j], cluster_x[j], cluster_y[key]), fill=(0, 0, 0), width=10)
		draw.line((cluster_x[i], cluster_y[key], cluster_x[j], cluster_y[key]), fill=(0, 0, 0), width=10)

		round_num = 3
		# i について
		value = round(table_d[(i,j)] / 2 - cluster_stack[i], round_num)
		value_text = str(value)
		size = font.getsize(value_text)
		value_x = cluster_x[i] - int(size[0]*1.05)
		value_y = int((cluster_y[i] + cluster_y[key]) / 2)
		draw.text((value_x, value_y), value_text, font=font, fill='#0000ff')

		# jについて
		value = round(table_d[(i,j)] / 2 - cluster_stack[j], round_num)
		value_text = str(value)
		size = font.getsize(value_text)
		value_x = cluster_x[j] - int(size[0]*1.05)
		value_y = int((cluster_y[j] + cluster_y[key]) / 2)
		draw.text((value_x, value_y), value_text, font=font, fill='#0000ff')


		ignoring_keys.append(key)
		attension_values.append(key)


	font = ImageFont.truetype("arial.ttf", 64) # font size is 64
	alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for i in range(original_length):
		# ラベル辞書を使えば数字以外も扱える
		text = alphabet[i]
		size = font.getsize(text)

		left_x = cluster_x[i] - (size[0] / 2)
		print(left_x)
		top_y = top_padding + main_frame_height

		# 画像右下に'Sampleと表示' #FFFは文字色（白）
		draw.text((left_x, top_y), text, font=font, fill='#000000')





	# ファイルを保存
	img.save('out.png', 'PNG', quality=100, optimize=True)







	input("push enter")





if __name__ == "__main__":
	main()