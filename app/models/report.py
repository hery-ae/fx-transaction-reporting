from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from ..database import Base

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(11), nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    transaction_date = Column(String(15), nullable=False)
    corporate_id = Column(Integer, nullable=False)
    corporate_name = Column(String(56), nullable=False)
    platform = Column(String(25), nullable=False)
    deal_type = Column(String(8), nullable=False)
    direction = Column(String(12), nullable=False)
    base_currency = Column(String(3), nullable=False)
    quote_currency = Column(String(3), nullable=False)
    base_volume = Column(Numeric(16, 2), nullable=False)
    quote_volume = Column(Numeric(16, 2), nullable=False)
    periods = Column(Integer, nullable=False)
    near_rate = Column(Numeric(16, 4), nullable=False)
    far_rate = Column(Numeric(16, 4))
    near_value_date = Column(String(15), nullable=False)
    far_value_date = Column(String(15))
    confirmed_at = Column(String(15), nullable=False)
    confirmed_by = Column(String(30), nullable=False)
    trader_id = Column(Integer, nullable=False)
    trader_name = Column(String(20), nullable=False)
    transaction_purpose = Column(String(40), nullable=False)
    status_code = Column(Integer, nullable=False)
    status_text = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(
        self,
        id=None,
        user_id=None,
        transaction_id=None,
        transaction_date=None,
        corporate_id=None,
        corporate_name=None,
        platform=None,
        deal_type=None,
        direction=None,
        base_currency=None,
        quote_currency=None,
        base_volume=None,
        quote_volume=None,
        periods=None,
        near_rate=None,
        far_rate=None,
        near_value_date=None,
        far_value_date=None,
        confirmed_at=None,
        confirmed_by=None,
        trader_id=None,
        trader_name=None,
        transaction_purpose=None,
        status_code=None,
        status_text=None
    ):
        self.id = id
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.transaction_date = transaction_date
        self.corporate_id = corporate_id
        self.corporate_name = corporate_name
        self.platform = platform
        self.deal_type = deal_type
        self.direction = direction
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.base_volume = base_volume
        self.quote_volume = quote_volume
        self.periods = periods
        self.near_rate = near_rate
        self.far_rate = far_rate
        self.near_value_date = near_value_date
        self.far_value_date = far_value_date
        self.confirmed_at = confirmed_at
        self.confirmed_by = confirmed_by
        self.trader_id = trader_id
        self.trader_name = trader_name
        self.transaction_purpose = transaction_purpose
        self.status_code = status_code
        self.status_text = status_text
