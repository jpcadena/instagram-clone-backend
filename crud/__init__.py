"""
CRUD module
"""
from typing import Any
from beanie import PydanticObjectId


class Specification:
    """
    Specification class
    """

    def __init__(self, value: Any):
        self.value: Any = value


class Filter:
    """
    Filter class
    """

    async def filter(self, spec: Specification):
        """
        Filter method
        :param spec: specification to filter by
        :type spec: Specification
        :return: None
        :rtype: NoneType
        """


class IdSpecification(Specification):
    """
    ID Specification class based on Specification
    """

    def __init__(self, document_id: PydanticObjectId):
        super().__init__(document_id)
        self.document_id: PydanticObjectId = document_id
