import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.time.LocalDate;

public class OrderController implements ActionListener {
    private OrderView view;
    private Order order = null;

    public OrderController(OrderView view) {
        this.view = view;

        view.getBtnAdd().addActionListener(this);
        view.getBtnPay().addActionListener(this);

        order = new Order();

    }


    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == view.getBtnAdd())
            addProduct();
        else
        if (e.getSource() == view.getBtnPay())
            makeOrder();
    }

    private void makeOrder() {
        if (order.getLines().isEmpty()) {
            JOptionPane.showMessageDialog(null, "No items in the current order!");
            return;
        }

        int nextOrderID = Application.getInstance().getDataAdapter().getNextOrderID();
        if (nextOrderID < 0) {
            JOptionPane.showMessageDialog(null, "Could not generate a new order ID!");
            return;
        }

        order.setOrderID(nextOrderID);
        order.setBuyerID(Application.getInstance().getCurrentUser().getUserID());
        order.setDate(LocalDate.now().toString());
        order.setTotalTax(order.getTotalCost() * 0.1);

        for (OrderLine line : order.getLines()) {
            line.setOrderID(order.getOrderID());

            Product product = Application.getInstance().getDataAdapter().loadProduct(line.getProductID());
            if (product == null) {
                JOptionPane.showMessageDialog(null, "Product " + line.getProductID() + " no longer exists.");
                return;
            }

            double newQuantity = product.getQuantity() - line.getQuantity();
            if (newQuantity < 0) {
                JOptionPane.showMessageDialog(null, "Insufficient inventory for product " + line.getProductID() + ".");
                return;
            }

            if (!Application.getInstance().getDataAdapter().updateProductQuantity(line.getProductID(), newQuantity)) {
                JOptionPane.showMessageDialog(null, "Failed to update inventory for product " + line.getProductID() + ".");
                return;
            }
        }

        if (!Application.getInstance().getDataAdapter().saveOrder(order)) {
            JOptionPane.showMessageDialog(null, "Could not save this order to the database!");
            return;
        }

        JOptionPane.showMessageDialog(null,
                "Order #" + order.getOrderID() + " placed. Total: $" + order.getTotalCost() +
                        ", Tax: $" + order.getTotalTax());

        this.view.clearRows();
        this.view.getLabTotal().setText("Total: ");
        this.order = new Order();
        this.view.setVisible(false);

    }

    private void addProduct() {
        String id = JOptionPane.showInputDialog("Enter ProductID: ");
        Product product = Application.getInstance().getDataAdapter().loadProduct(Integer.parseInt(id));
        if (product == null) {
            JOptionPane.showMessageDialog(null, "This product does not exist!");
            return;
        }

        double quantity = Double.parseDouble(JOptionPane.showInputDialog(null,"Enter quantity: "));

        if (quantity < 0 || quantity > product.getQuantity()) {
            JOptionPane.showMessageDialog(null, "This quantity is not valid!");
            return;
        }

        OrderLine line = new OrderLine();
        line.setOrderID(this.order.getOrderID());
        line.setProductID(product.getProductID());
        line.setQuantity(quantity);
        line.setCost(quantity * product.getPrice());
        order.getLines().add(line);
        order.setTotalCost(order.getTotalCost() + line.getCost());



        Object[] row = new Object[5];
        row[0] = line.getProductID();
        row[1] = product.getName();
        row[2] = product.getPrice();
        row[3] = line.getQuantity();
        row[4] = line.getCost();

        this.view.addRow(row);
        this.view.getLabTotal().setText("Total: $" + order.getTotalCost());
        this.view.invalidate();
    }

}