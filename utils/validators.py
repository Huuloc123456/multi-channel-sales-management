def validate_product_data(name, price, stock):
    if not name or len(name.strip()) == 0:
        return False, "Tên sản phẩm không được để trống!"
    
    try:
        p = float(price)
        if p <= 0: return False, "Giá sản phẩm phải lớn hơn 0!"
    except ValueError:
        return False, "Giá sản phẩm phải là số!"
        
    try:
        s = int(stock)
        if s < 0: return False, "Số lượng không được âm!"
    except ValueError:
        return False, "Số lượng phải là số nguyên!"
        
    return True, "Hợp lệ"