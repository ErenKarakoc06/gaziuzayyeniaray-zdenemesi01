    def optimize_time(self):
        points = np.array([[wp['lat'], wp['lon'], wp['alt']] for wp in self.waypoints])
        n_points = len(points)
        
        def calculate_time(ordered_points):
            total_time = 0
            speed = 15  # m/s varsayılan hız
            
            for i in range(len(ordered_points)-1):
                # 3B mesafe hesapla
                dist = np.sqrt(np.sum((ordered_points[i] - ordered_points[i+1])**2))
                # Yükseklik değişimi için ek süre
                alt_diff = abs(ordered_points[i][2] - ordered_points[i+1][2])
                vertical_time = alt_diff / 5  # 5 m/s dikey hız
                
                # Toplam süreyi hesapla
                segment_time = dist/speed + vertical_time
                total_time += segment_time
                
                # Bekleme süresini ekle
                total_time += self.waypoints[i]['hold_time']
            
            return total_time

        # Başlangıç çözümü
        x0 = np.arange(n_points)
        
        def objective(order):
            ordered_points = points[order.astype(int)]
            return calculate_time(ordered_points)

        # Optimizasyon
        result = minimize(objective, x0, method='SLSQP')
        optimal_order = result.x.astype(int)

        return [self.waypoints[i] for i in optimal_order]

    def optimize_energy(self):
        points = np.array([[wp['lat'], wp['lon'], wp['alt']] for wp in self.waypoints])
        n_points = len(points)
        
        def calculate_energy(ordered_points):
            total_energy = 0
            base_power = 100  # Watt, hovering için temel güç tüketimi
            
            for i in range(len(ordered_points)-1):
                # Yatay ve dikey hareket için enerji hesapla
                dist = np.sqrt(np.sum((ordered_points[i] - ordered_points[i+1])**2))
                alt_diff = ordered_points[i+1][2] - ordered_points[i][2]
                
                # Yükselme için daha fazla enerji gerekir
                if alt_diff > 0:
                    vertical_power = base_power * 1.5
                else:
                    vertical_power = base_power * 0.8
                
                # Toplam enerjiyi hesapla (Joule)
                segment_energy = base_power * (dist/15)  # 15 m/s hızla
                vertical_energy = vertical_power * (abs(alt_diff)/5)  # 5 m/s dikey hız
                total_energy += segment_energy + vertical_energy
                
                # Bekleme enerjisini ekle
                total_energy += base_power * self.waypoints[i]['hold_time']
            
            return total_energy

        def objective(order):
            ordered_points = points[order.astype(int)]
            return calculate_energy(ordered_points)

        x0 = np.arange(n_points)
        result = minimize(objective, x0, method='SLSQP')
        optimal_order = result.x.astype(int)

        return [self.waypoints[i] for i in optimal_order]

    def optimize_coverage(self):
        # Alan kapsama optimizasyonu
        coverage_radius = 20  # metre
        grid_size = 5  # metre
        
        # Çalışma alanı sınırlarını belirle
        lats = [wp['lat'] for wp in self.waypoints]
        lons = [wp['lon'] for wp in self.waypoints]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Grid oluştur
        lat_grid = np.arange(min_lat, max_lat, grid_size/111111)  # yaklaşık metre to derece
        lon_grid = np.arange(min_lon, max_lon, grid_size/(111111*np.cos(np.radians(min_lat))))
        
        grid_points = np.array([(lat, lon) for lat in lat_grid for lon in lon_grid])
        
        def calculate_coverage(ordered_points):
            coverage = np.zeros(len(grid_points))
            
            for point in ordered_points:
                # Her grid noktası için kapsama kontrolü
                distances = np.sqrt(np.sum((grid_points - point[:2])**2, axis=1))
                coverage[distances <= coverage_radius/111111] = 1
            
            return -np.sum(coverage)  # Negatif değer, çünkü minimize ediyoruz

        def objective(order):
            ordered_points = points[order.astype(int)]
            return calculate_coverage(ordered_points)

        points = np.array([[wp['lat'], wp['lon']] for wp in self.waypoints])
        x0 = np.arange(len(points))
        result = minimize(objective, x0, method='SLSQP')
        optimal_order = result.x.astype(int)

        return [self.waypoints[i] for i in optimal_order]

    def update_route_table(self, optimized_route):
        self.waypoint_table.setRowCount(0)
        for i, wp in enumerate(optimized_route):
            self.add_waypoint(wp['lat'], wp['lon'], wp['alt'], wp['hold_time'])

    def clear_route(self):
        self.waypoint_table.setRowCount(0)
        self.waypoints = []
        self.route_updated.emit([])

    def add_constraint(self, constraint_type, value):
        self.constraints.append({
            'type': constraint_type,
            'value': value
        })

    def add_obstacle(self, lat, lon, radius, height):
        self.obstacles.append({
            'lat': lat,
            'lon': lon,
            'radius': radius,
            'height': height
        })