import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Application {

    private static Application instance;   // Singleton pattern

    public static Application getInstance() {
        if (instance == null) {
            instance = new Application();
        }
        return instance;
    }
    // Main components of this application

    private Connection connection;

    public Connection getDBConnection() {
        return connection;
    }

    private DataAdapter dataAdapter;

    private User currentUser = null;

    public User getCurrentUser() { return currentUser; }

    public void setCurrentUser(User user) {
        this.currentUser = user;
    }

    private ProductView productView = new ProductView();

    private OrderView orderView = new OrderView();

    private MainScreen mainScreen = new MainScreen();

    public MainScreen getMainScreen() {
        return mainScreen;
    }

    public ProductView getProductView() {
        return productView;
    }

    public OrderView getOrderView() {
        return orderView;
    }

    public LoginScreen loginScreen = new LoginScreen();

    public LoginScreen getLoginScreen() {
        return loginScreen;
    }

    public LoginController loginController;

    private ProductController productController;

    public ProductController getProductController() {
        return productController;
    }

    private OrderController orderController;

    public OrderController getOrderController() {
        return orderController;
    }

    public DataAdapter getDataAdapter() {
        return dataAdapter;
    }


    private Application() {
        String dataMode = System.getenv().getOrDefault("STOREAPP_DATA_MODE", "rest").trim().toLowerCase();

        if ("jdbc".equals(dataMode)) {
            try {
                String dbType = System.getenv().getOrDefault("STOREAPP_DB", "mysql").trim().toLowerCase();

                if ("sqlite".equals(dbType)) {
                    Class.forName("org.sqlite.JDBC");
                    String sqlitePath = System.getenv().getOrDefault("STOREAPP_SQLITE_PATH", "store.db");
                    String url = "jdbc:sqlite:" + sqlitePath;
                    connection = DriverManager.getConnection(url);
                }
                else {
                    Class.forName("com.mysql.cj.jdbc.Driver");
                    String host = System.getenv().getOrDefault("STOREAPP_DB_HOST", "localhost");
                    String port = System.getenv().getOrDefault("STOREAPP_DB_PORT", "3306");
                    String database = System.getenv().getOrDefault("STOREAPP_DB_NAME", "storeapp");
                    String user = System.getenv().getOrDefault("STOREAPP_DB_USER", "root");
                    String password = System.getenv().getOrDefault("STOREAPP_DB_PASSWORD", "");
                    String url = "jdbc:mysql://" + host + ":" + port + "/" + database + "?serverTimezone=UTC";
                    connection = DriverManager.getConnection(url, user, password);
                }

                dataAdapter = new DataAdapter(connection);
            }
            catch (ClassNotFoundException ex) {
                System.out.println("JDBC driver is not installed. System exits with error!");
                ex.printStackTrace();
                System.exit(1);
            }
            catch (SQLException ex) {
                System.out.println("Database is not ready. System exits with error!" + ex.getMessage());
                ex.printStackTrace();
                System.exit(2);
            }
        } else {
            dataAdapter = new DataAdapter();
        }

        productController = new ProductController(productView);

        orderController = new OrderController(orderView);

        loginController = new LoginController(loginScreen);
    }


    public static void main(String[] args) {
        Application.getInstance().getLoginScreen().setVisible(true);
    }
}
