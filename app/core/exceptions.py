class UserNotFoundException(Exception):
    pass


class CartAlreadyExistsException(Exception):
    pass


class CartNotFoundException(Exception):
    pass


class CartAlreadyCheckedOutException(Exception):
    pass


class CartEmptyException(Exception):
    pass


class VariantNotFoundException(Exception):
    pass


class CartItemNotFoundException(Exception):
    pass


class InsufficientStockException(Exception):
    pass


class DatabaseException(Exception):
    pass
