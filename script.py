import pkg_resources

try:
    version = pkg_resources.get_distribution("python-decouple").version
    print(f"python-decouple version: {version}")
except pkg_resources.DistributionNotFound:
    print("python-decouple no está instalado.")
