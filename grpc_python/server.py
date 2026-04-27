from concurrent import futures
import time

import grpc

import route_guide_pb2
import route_guide_pb2_grpc
from route_guide_resources import get_distance, get_feature, read_route_guide_database


class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.db = read_route_guide_database()
        self.notes = {}

    def GetFeature(self, request, context):
        feature = get_feature(self.db, request)
        if feature is None:
            return route_guide_pb2.Feature(name="", location=request)
        return feature

    def ListFeatures(self, request, context):
        left = min(request.lo.longitude, request.hi.longitude)
        right = max(request.lo.longitude, request.hi.longitude)
        bottom = min(request.lo.latitude, request.hi.latitude)
        top = max(request.lo.latitude, request.hi.latitude)

        for feature in self.db:
            location = feature.location
            if (
                left <= location.longitude <= right
                and bottom <= location.latitude <= top
            ):
                yield feature

    def RecordRoute(self, request_iterator, context):
        point_count = 0
        feature_count = 0
        distance = 0
        previous = None
        start_time = time.time()

        for point in request_iterator:
            point_count += 1
            if get_feature(self.db, point) is not None:
                feature_count += 1
            if previous is not None:
                distance += get_distance(previous, point)
            previous = point

        return route_guide_pb2.RouteSummary(
            point_count=point_count,
            feature_count=feature_count,
            distance=distance,
            elapsed_time=int(time.time() - start_time),
        )

    def RouteChat(self, request_iterator, context):
        for note in request_iterator:
            key = (note.location.latitude, note.location.longitude)
            previous_notes = self.notes.get(key, [])
            for previous_note in previous_notes:
                yield previous_note
            self.notes.setdefault(key, []).append(note)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(RouteGuideServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Serveur Python gRPC en ecoute sur localhost:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
