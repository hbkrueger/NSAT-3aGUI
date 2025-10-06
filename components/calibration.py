import nau7802_generator as nau
import statistics

# Keep the first y value as 0 and add the rest of your known weights in grams
x = []
y = [0, 100, 200, 300, 400]

sps = 320 # samples per second of nau7802
cal_time = 10 # calibration time in seconds

spc = sps*cal_time # samples per calibration

gen = nau.generator()

print("Initializing sensor")
print("Garbage reading: ", next(gen))


print("\nKeep weight off cell.")
input("Press Enter to begin offset calculation.")
print("Calculating offset...")



val = []
for i in range(spc):
	val.append(next(gen))
	print("[",i+1,"/",spc,"]",val[-1])

x_o = statistics.mean(val)
print("Offset is:", x_o)

print("\nDon't put any weight on cell.")
input("Press Enter when done...")
print("Taring cell...")

val = []
for i in range(spc):
	val.append(next(gen) - x_o)
	print("[",i+1,"/",spc,"]",val[-1])

x.append( statistics.mean(val) )
print("Added", x[-1], "to x.")


for i in range(len(y) - 1):
	
	print("\nPut a",y[i+1], "gram weight on cell.")
	
	input("Press Enter when done...")
	print("Average values...")

	val = []
	for i in range(spc):
		val.append(next(gen) - x_o)
		print("[",i+1,"/",spc,"]",val[-1])

	x.append( statistics.mean(val) ) 
	print("Added", x[-1], "to x.")


reg = statistics.linear_regression(x, y)
print("\n\n======================================================================================\n")
print("Calibration formula:", reg )
print("\n======================================================================================")


with open("calibration.txt", "w") as f:

	f.write(f"x_o={x_o}\n")
	f.write(",".join(map(str, x)))
	f.write("\n")
	f.write(",".join(map(str, y)))
	f.write("\n")
	f.write(f"Slope: {reg.slope}\n")
	f.write(f"Intercept: {reg.intercept}\n")
