class PackageBuilder:
    """

    """
    @staticmethod
    def build_arduino_package(payload):
        """
        1 2 [payload length (1 byte)] [payload (max 20 bytes)] [2 bytes checksum?] 3 4
        :return:
        """

        package = [1, 2, len(payload)]
        for item in payload:
            package.append(int(item))
        package.append(3)
        package.append(4)
        return package
