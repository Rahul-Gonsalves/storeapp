import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DataAdapter {
    private final String baseUrl;
    private final HttpClient client;

    public DataAdapter() {
        this(null);
    }

    public DataAdapter(Connection ignoredConnection) {
        this.baseUrl = System.getenv().getOrDefault("STOREAPP_API_BASE_URL", "http://127.0.0.1:9000");
        this.client = HttpClient.newHttpClient();
    }

    public Product loadProduct(int id) {
        try {
            HttpResult result = send("GET", "/products/" + id, null);
            if (result.statusCode == 404) return null;
            if (result.statusCode != 200) throw new RuntimeException(result.body);

            Product product = new Product();
            product.setProductID(extractInt(result.body, "ProductID"));
            product.setName(extractString(result.body, "ProductName"));
            product.setPrice(extractDouble(result.body, "Price"));
            product.setQuantity(extractDouble(result.body, "Quantity"));
            product.setSellerID(extractOptionalInt(result.body, "SellerID", 0));
            return product;
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return null;
        }
    }

    public boolean saveProduct(Product product) {
        try {
            String body = "{"
                    + "\"ProductID\":" + product.getProductID() + ","
                    + "\"ProductName\":\"" + escape(product.getName()) + "\","
                    + "\"Price\":" + product.getPrice() + ","
                    + "\"Quantity\":" + product.getQuantity() + ","
                    + "\"SellerID\":" + product.getSellerID()
                    + "}";
            HttpResult result = send("POST", "/products/" + product.getProductID(), body);
            return result.statusCode == 200;
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return false;
        }
    }

    public Order loadOrder(int id) {
        try {
            HttpResult result = send("GET", "/orders/" + id, null);
            if (result.statusCode == 404) return null;
            if (result.statusCode != 200) throw new RuntimeException(result.body);

            Order order = new Order();
            order.setOrderID(extractInt(result.body, "OrderID"));
            order.setBuyerID(extractOptionalInt(result.body, "UserID", extractOptionalInt(result.body, "BuyerID", 0)));
            order.setTotalCost(extractDouble(result.body, "TotalCost"));
            order.setTotalTax(extractOptionalDouble(result.body, "TotalTax", 0.0));
            order.setDate(extractString(result.body, "OrderDate"));

            Matcher detailsMatcher = Pattern.compile("\"Details\"\\s*:\\s*\\[(.*)]", Pattern.DOTALL).matcher(result.body);
            if (detailsMatcher.find()) {
                Matcher itemMatcher = Pattern.compile("\\{[^{}]*}").matcher(detailsMatcher.group(1));
                while (itemMatcher.find()) {
                    String item = itemMatcher.group();
                    OrderLine line = new OrderLine();
                    line.setOrderID(order.getOrderID());
                    line.setProductID(extractInt(item, "ProductID"));
                    line.setQuantity(extractDouble(item, "Quantity"));
                    line.setCost(extractDouble(item, "Cost"));
                    order.addLine(line);
                }
            }
            return order;
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return null;
        }
    }

    public boolean saveOrder(Order order) {
        try {
            StringBuilder details = new StringBuilder("[");
            for (int i = 0; i < order.getLines().size(); i++) {
                OrderLine line = order.getLines().get(i);
                if (i > 0) details.append(",");
                details.append("{")
                        .append("\"ProductID\":").append(line.getProductID()).append(",")
                        .append("\"Quantity\":").append(line.getQuantity()).append(",")
                        .append("\"Cost\":").append(line.getCost())
                        .append("}");
            }
            details.append("]");

            String body = "{"
                    + "\"OrderID\":" + order.getOrderID() + ","
                    + "\"UserID\":" + order.getBuyerID() + ","
                    + "\"OrderDate\":\"" + escape(order.getDate()) + "\","
                    + "\"TotalCost\":" + order.getTotalCost() + ","
                    + "\"TotalTax\":" + order.getTotalTax() + ","
                    + "\"Details\":" + details
                    + "}";
            HttpResult result = send("POST", "/orders/" + order.getOrderID(), body);
            return result.statusCode == 200;
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return false;
        }
    }

    public int getNextOrderID() {
        try {
            HttpResult result = send("GET", "/orders/next-id", null);
            if (result.statusCode != 200) throw new RuntimeException(result.body);
            return extractInt(result.body, "nextOrderID");
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return -1;
        }
    }

    public boolean updateProductQuantity(int productID, double newQuantity) {
        Product product = loadProduct(productID);
        if (product == null) return false;
        product.setQuantity(newQuantity);
        return saveProduct(product);
    }

    public User loadUser(String username, String password) {
        try {
            String body = "{"
                    + "\"username\":\"" + escape(username) + "\","
                    + "\"password\":\"" + escape(password) + "\""
                    + "}";
            HttpResult result = send("POST", "/users/login", body);
            if (result.statusCode == 404) return null;
            if (result.statusCode != 200) throw new RuntimeException(result.body);

            User user = new User();
            user.setUserID(extractInt(result.body, "UserID"));
            user.setUsername(extractString(result.body, "UserName"));
            user.setPassword(extractString(result.body, "Password"));
            user.setFullName(extractString(result.body, "DisplayName"));
            return user;
        } catch (Exception e) {
            System.out.println("API access error!");
            e.printStackTrace();
            return null;
        }
    }

    private HttpResult send(String method, String path, String body) throws IOException, InterruptedException {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .header("Accept", "application/json");
        if (body == null) {
            builder.method(method, HttpRequest.BodyPublishers.noBody());
        } else {
            builder.header("Content-Type", "application/json");
            builder.method(method, HttpRequest.BodyPublishers.ofString(body));
        }
        HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        return new HttpResult(response.statusCode(), response.body());
    }

    private int extractInt(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(-?\\d+)").matcher(json);
        if (!matcher.find()) throw new RuntimeException("Missing integer field: " + field);
        return Integer.parseInt(matcher.group(1));
    }

    private int extractOptionalInt(String json, String field, int defaultValue) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(-?\\d+)").matcher(json);
        return matcher.find() ? Integer.parseInt(matcher.group(1)) : defaultValue;
    }

    private double extractDouble(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(-?\\d+(?:\\.\\d+)?)").matcher(json);
        if (!matcher.find()) throw new RuntimeException("Missing numeric field: " + field);
        return Double.parseDouble(matcher.group(1));
    }

    private double extractOptionalDouble(String json, String field, double defaultValue) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*(-?\\d+(?:\\.\\d+)?)").matcher(json);
        return matcher.find() ? Double.parseDouble(matcher.group(1)) : defaultValue;
    }

    private String extractString(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + Pattern.quote(field) + "\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"").matcher(json);
        if (!matcher.find()) throw new RuntimeException("Missing string field: " + field);
        return matcher.group(1).replace("\\\"", "\"").replace("\\\\", "\\");
    }

    private String escape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static class HttpResult {
        private final int statusCode;
        private final String body;

        private HttpResult(int statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body;
        }
    }
}
