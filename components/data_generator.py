import wt901c_generator as wt901c
import nau7802_generator as nau7802
import time



def generator(target_hz: float = 200.0, imu_gen=None, lc_gen=None):
	imu = imu_gen or wt901c.generator()
	load_cell = lc_gen or nau7802.generator()
	
	dt = 1.0 / target_hz
	next_t = time.perf_counter()
	
	while True:
	
		now = time.perf_counter()
		
		while next_t <= now:
			next_t += dt
			
		sleep_for = next_t - now
		if sleep_for > 0:
			time.sleep(sleep_for)
			
		ts = time.perf_counter()
	
		imu_d = next(imu)
		lc_d = next(load_cell)
	
		yield {
			"ts": ts, 
			"ax": imu_d[0], 
			"ay": imu_d[1], 
			"az": imu_d[2], 
			"gx": imu_d[3], 
			"gy": imu_d[4], 
			"gz": imu_d[5], 
			"roll": imu_d[6],
			"pitch": imu_d[7], 
			"yaw": imu_d[8], 
			"Newtons": lc_d 
		}
		
