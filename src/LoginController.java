import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class LoginController implements ActionListener {
    private LoginScreen loginScreen;

    public LoginController(LoginScreen loginScreen) {
        this.loginScreen = loginScreen;
        this.loginScreen.getBtnLogin().addActionListener(this);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == loginScreen.getBtnLogin()) {
            String username = loginScreen.getTxtUserName().getText().trim();
            String password = loginScreen.getTxtPassword().getText().trim();

            System.out.println("Login with username = " + username + " and password = " + password);
            User user = Application.getInstance().getDataAdapter().loadUser(username, password);

            if (user == null) { // No such user exists
                JOptionPane.showMessageDialog(null, "This user does not exist!");
            }
            else {
                Application.getInstance().setCurrentUser(user);
                this.loginScreen.setVisible(false);
                Application.getInstance().getMainScreen().setVisible(true);
            }
        }
    }
}
