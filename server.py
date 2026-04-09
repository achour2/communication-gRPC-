import grpc
from concurrent import futures
import time
import json

import route_guide_pb2
import route_guide_pb2_grpc


def read_route_guide_database():
    with open("route_guide_db.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    features = []
    for item in data:
        feature = route_guide_pb2.Feature(
            name=item["name"],
            location=route_guide_pb2.Point(
                latitude=item["location"]["latitude"],
                longitude=item["location"]["longitude"]
            )
        )
        features.append(feature)
    return features


class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.db = read_route_guide_database()
        self.notes = {}

    def GetFeature(self, request, context):
        for feature in self.db:
            if feature.location.latitude == request.latitude and feature.location.longitude == request.longitude:
                return feature
        return route_guide_pb2.Feature(name="", location=request)

    def ListFeatures(self, request, context):
        left = min(request.lo.longitude, request.hi.longitude)
        right = max(request.lo.longitude, request.hi.longitude)
        bottom = min(request.lo.latitude, request.hi.latitude)
        top = max(request.lo.latitude, request.hi.latitude)

        for feature in self.db:
            if left <= feature.location.longitude <= right and bottom <= feature.location.latitude <= top:
                yield feature

    def RecordRoute(self, request_iterator, context):
        point_count = 0
        feature_count = 0

        for point in request_iterator:
            point_count += 1
            for feature in self.db:
                if feature.location.latitude == point.latitude and feature.location.longitude == point.longitude:
                    feature_count += 1
                    break

        return route_guide_pb2.RouteSummary(
            point_count=point_count,
            feature_count=feature_count,
            distance=0,
            elapsed_time=0
        )

    def RouteChat(self, request_iterator, context):
        for note in request_iterator:
            key = (note.location.latitude, note.location.longitude)

            if key not in self.notes:
                self.notes[key] = []

            for prev_note in self.notes[key]:
                yield prev_note

            self.notes[key].append(note)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(RouteGuideServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Serveur Python lancé sur le port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()