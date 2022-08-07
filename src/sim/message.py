class Message:
    def __init__(
        self,
        _id: str,
        src_id: int = None,
        dst_id: int = None,
    ):
        self._id = _id
        self.src_id = src_id
        self.dst_id = dst_id

    def __repr__(self):
        # return (
        #     "Msg( \n"
        #     f"\t id= {self._id} \n"
        #     f"\t src_id= {self.src_id} \n"
        #     f"\t dst_id= {self.dst_id} \n"
        #     ")"
        # )

        return f"Message(id= {self._id})"
