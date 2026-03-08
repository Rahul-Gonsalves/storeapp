//java OrderApiServer.java
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class OrderApiServer {
    private static final String DB_PATH = System.getenv().getOrDefault("ORDER_API_DB", "store.db");
    private static final String HOST = System.getenv().getOrDefault("ORDER_API_HOST", "127.0.0.1");
    private static final int PORT = Integer.parseInt(System.getenv().getOrDefault("ORDER_API_PORT", "8080"));

    public static void main(String[] args) throws Exception {
        Class.forName("org.sqlite.JDBC");
        HttpServer server = HttpServer.create(new InetSocketAddress(HOST, PORT), 0);
        server.createContext("/api/orders", OrderApiServer::handleOrder);
        server.start();
        System.out.println("Order API running at http://" + HOST + ":" + PORT + " (GET /api/orders/<id>)");
    }

    private static void handleOrder(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            write(exchange, 405, "{\"error\":\"Method not allowed\"}");
            return;
        }

        String path = exchange.getRequestURI().getPath();
        if ("/api/orders".equals(path) || "/api/orders/".equals(path)) {
            write(exchange, 400, "{\"error\":\"Use /api/orders/<id>\"}");
            return;
        }
        if (!path.startsWith("/api/orders/")) {
            write(exchange, 404, "{\"error\":\"Endpoint not found\"}");
            return;
        }

        String idText = path.substring("/api/orders/".length());
        if (!idText.matches("\\d+")) {
            write(exchange, 400, "{\"error\":\"Order ID must be a positive integer\"}");
            return;
        }

        int orderId = Integer.parseInt(idText);
        try {
            String json = fetchOrderJson(orderId);
            if (json == null) {
                write(exchange, 404, "{\"error\":\"Order not found\",\"OrderID\":" + orderId + "}");
                return;
            }
            write(exchange, 200, json);
        } catch (SQLException e) {
            e.printStackTrace();
            write(exchange, 500, "{\"error\":\"Database error\"}");
        }
    }

    private static String fetchOrderJson(int orderId) throws SQLException {
        try (Connection c = DriverManager.getConnection("jdbc:sqlite:" + DB_PATH)) {
            String header;
            try (PreparedStatement s = c.prepareStatement(
                    "SELECT OrderID, OrderDate, CustomerID, TotalCost, TotalTax FROM Orders WHERE OrderID = ?")) {
                s.setInt(1, orderId);
                try (ResultSet r = s.executeQuery()) {
                    if (!r.next()) return null;
                    header = "\"OrderID\":" + r.getInt("OrderID")
                            + ",\"OrderDate\":\"" + esc(r.getString("OrderDate")) + "\""
                            + ",\"CustomerID\":" + intOrNull(r, "CustomerID")
                            + ",\"TotalCost\":" + dblOrNull(r, "TotalCost")
                            + ",\"TotalTax\":" + dblOrNull(r, "TotalTax");
                }
            }

            StringBuilder details = new StringBuilder("[");
            try (PreparedStatement s = c.prepareStatement(
                    "SELECT ProductID, Quantity, Cost FROM OrderLine WHERE OrderID = ? ORDER BY ProductID")) {
                s.setInt(1, orderId);
                try (ResultSet r = s.executeQuery()) {
                    boolean first = true;
                    while (r.next()) {
                        if (!first) details.append(',');
                        first = false;
                        details.append("{\"ProductID\":").append(r.getInt("ProductID"))
                                .append(",\"Quantity\":").append(dblOrNull(r, "Quantity"))
                                .append(",\"Cost\":").append(dblOrNull(r, "Cost")).append('}');
                    }
                }
            }
            details.append(']');
            return "{" + header + ",\"Details\":" + details + "}";
        }
    }

    private static String dblOrNull(ResultSet r, String col) throws SQLException {
        double v = r.getDouble(col);
        return r.wasNull() ? "null" : Double.toString(v);
    }

    private static String intOrNull(ResultSet r, String col) throws SQLException {
        int v = r.getInt(col);
        return r.wasNull() ? "null" : Integer.toString(v);
    }

    private static String esc(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static void write(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }
}
