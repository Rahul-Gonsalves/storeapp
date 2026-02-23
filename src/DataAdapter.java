import java.sql.*;

public class DataAdapter {
    private Connection connection;

    public DataAdapter(Connection connection) {
        this.connection = connection;
    }

    public Product loadProduct(int id) {
        try {
            String query = "SELECT ProductID, Name, Price, Quantity, SellerID FROM Products WHERE ProductID = " + id;

            Statement statement = connection.createStatement();
            ResultSet resultSet = statement.executeQuery(query);
            if (resultSet.next()) {
                Product product = new Product();
                product.setProductID(resultSet.getInt(1));
                product.setName(resultSet.getString(2));
                product.setPrice(resultSet.getDouble(3));
                product.setQuantity(resultSet.getDouble(4));
                product.setSellerID(resultSet.getInt(5));
                resultSet.close();
                statement.close();

                return product;
            }

        } catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
        }
        return null;
    }

    public boolean saveProduct(Product product) {
        try {
            PreparedStatement statement = connection.prepareStatement("SELECT * FROM Products WHERE ProductID = ?");
            statement.setInt(1, product.getProductID());

            ResultSet resultSet = statement.executeQuery();

            if (resultSet.next()) { // this product exists, update its fields
                statement = connection.prepareStatement("UPDATE Products SET Name = ?, Price = ?, Quantity = ?, SellerID = ? WHERE ProductID = ?");
                statement.setString(1, product.getName());
                statement.setDouble(2, product.getPrice());
                statement.setDouble(3, product.getQuantity());
                statement.setInt(4, product.getSellerID());
                statement.setInt(5, product.getProductID());
            }
            else { // this product does not exist, use insert into
                statement = connection.prepareStatement("INSERT INTO Products (ProductID, Name, Price, Quantity, SellerID) VALUES (?, ?, ?, ?, ?)");
                statement.setInt(1, product.getProductID());
                statement.setString(2, product.getName());
                statement.setDouble(3, product.getPrice());
                statement.setDouble(4, product.getQuantity());
                statement.setInt(5, product.getSellerID());
            }
            statement.execute();
            resultSet.close();
            statement.close();
            return true;        // save successfully

        } catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
            return false; // cannot save!
        }
    }

    public Order loadOrder(int id) {
        try {
            Order order = null;
            Statement statement = connection.createStatement();
            ResultSet resultSet = statement.executeQuery("SELECT * FROM Orders WHERE OrderID = " + id);

            if (resultSet.next()) {
                order = new Order();
                order.setOrderID(resultSet.getInt("OrderID"));
                order.setBuyerID(resultSet.getInt("CustomerID"));
                order.setTotalCost(resultSet.getDouble("TotalCost"));
                order.setDate(resultSet.getString("OrderDate"));
            }
            resultSet.close();

            // loading the order lines for this order
            if (order != null) {
                resultSet = statement.executeQuery("SELECT * FROM OrderLine WHERE OrderID = " + id);

                while (resultSet.next()) {
                    OrderLine line = new OrderLine();
                    line.setOrderID(resultSet.getInt(1));
                    line.setProductID(resultSet.getInt(2));
                    line.setQuantity(resultSet.getDouble(3));
                    line.setCost(resultSet.getDouble(4));
                    order.addLine(line);
                }
                resultSet.close();
            }

            statement.close();

            return order;

        } catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
            return null;
        }
    }

    public boolean saveOrder(Order order) {
        try {
            PreparedStatement statement = connection.prepareStatement("INSERT INTO Orders (OrderID, OrderDate, CustomerID, TotalCost, TotalTax) VALUES (?, ?, ?, ?, ?)");
            statement.setInt(1, order.getOrderID());
            statement.setInt(3, order.getBuyerID());
            statement.setString(2, order.getDate());
            statement.setDouble(4, order.getTotalCost());
            statement.setDouble(5, order.getTotalTax());

            statement.execute();    // commit to the database;
            statement.close();

            statement = connection.prepareStatement("INSERT INTO OrderLine VALUES (?, ?, ?, ?)");

            for (OrderLine line: order.getLines()) { // store for each order line!
                statement.setInt(1, line.getOrderID());
                statement.setInt(2, line.getProductID());
                statement.setDouble(3, line.getQuantity());
                statement.setDouble(4, line.getCost());

                statement.execute();    // commit to the database;
            }
            statement.close();
            return true; // save successfully!
        }
        catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
            return false;
        }
    }

    public int getNextOrderID() {
        try {
            Statement statement = connection.createStatement();
            ResultSet resultSet = statement.executeQuery("SELECT COALESCE(MAX(OrderID), 0) + 1 FROM Orders");
            int nextId = 1;
            if (resultSet.next()) {
                nextId = resultSet.getInt(1);
            }
            resultSet.close();
            statement.close();
            return nextId;
        }
        catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
            return -1;
        }
    }

    public boolean updateProductQuantity(int productID, double newQuantity) {
        try {
            PreparedStatement statement = connection.prepareStatement("UPDATE Products SET Quantity = ? WHERE ProductID = ?");
            statement.setDouble(1, newQuantity);
            statement.setInt(2, productID);
            statement.execute();
            statement.close();
            return true;
        }
        catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
            return false;
        }
    }

    public User loadUser(String username, String password) {
        try {

            PreparedStatement statement = connection.prepareStatement("SELECT * FROM Users WHERE UserName = ? AND Password = ?");
            statement.setString(1, username);
            statement.setString(2, password);
            ResultSet resultSet = statement.executeQuery();
            if (resultSet.next()) {
                User user = new User();
                user.setUserID(resultSet.getInt("UserID"));
                user.setUsername(resultSet.getString("UserName"));
                user.setPassword(resultSet.getString("Password"));
                user.setFullName(resultSet.getString("DisplayName"));
                resultSet.close();
                statement.close();

                return user;
            }

        } catch (SQLException e) {
            System.out.println("Database access error!");
            e.printStackTrace();
        }
        return null;
    }
}
