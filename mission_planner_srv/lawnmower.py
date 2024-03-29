from swarm_interfaces.srv import MissionPlanningV2
from swarm_interfaces.msg import Mission, PlannedMissionV2, GeoPoint, Zone, ZoneTypeEnum, SubSwarmRoute

import rclpy
from rclpy.node import Node


publish_plan_topic = "mission_plan"

 
class LawnmowerPlanningService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(MissionPlanningV2, 'mission_planning', self.mission_planning_callback)  
        self.plan_publisher = self.create_publisher(PlannedMissionV2, publish_plan_topic, 10)  

    def mission_planning_callback(self, request, response):
        self.get_logger().info('Incoming request\na: %s' % str(request))
        
        mission = request.mission
        altitude = mission.initial_location[0].altitude + 1
        min_x = mission.zones[0].geo_points[0].latitude
        min_y = mission.zones[0].geo_points[0].longitude
        max_x = mission.zones[0].geo_points[3].latitude
        max_y = mission.zones[0].geo_points[3].longitude
        resolution = 0.5

        plan = []

        x = min_x
        while x < max_x:
            
            y = min_y
            while y < max_y:
                g = GeoPoint(altitude=altitude, latitude=x, longitude=y)
                plan.append(g)
                y = y + resolution            
            x = x + resolution

            if x > max_x:
                break

            y = max_y
            while y > min_y:
                g = GeoPoint(altitude=altitude, latitude=x, longitude=y)
                plan.append(g)
                y = y - resolution            
            x = x + resolution

        response.planned_mission = PlannedMissionV2()
        route = SubSwarmRoute()
        route.drones = mission.drones
        route.flight_altitude = 1.0
        route.route = plan
        response.planned_mission.routes.append(route)
        
        self.plan_publisher.publish(response.planned_mission)
        return response

def main(args=None):
    rclpy.init(args=args)

    planning_service = LawnmowerPlanningService()

    rclpy.spin(planning_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
