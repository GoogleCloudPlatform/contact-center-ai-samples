import mock


def patch_client(client, method_name, stack, return_value=None):
    stack.enter_context(
        mock.patch.object(
            client,
            method_name,
            return_value=return_value,
        )
    )
