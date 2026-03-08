import java.io.*;
import java.net.*;
import java.util.*;

class WebServer
{
 public static void main () throws Exception {
     String requestMessageLine;

     int myPort = 8080;

     // set up connection socket
     ServerSocket listenSocket = new ServerSocket(myPort);

     // listen (i.e. wait) for connection request
     System.out.println("Web server waiting for request on port " + myPort);

     while (true) {

         Socket connectionSocket = listenSocket.accept();


         // set up the read and write end of the communication socket
         BufferedReader inFromClient = new BufferedReader(
                 new InputStreamReader(connectionSocket.getInputStream()));
         DataOutputStream outToClient = new DataOutputStream(
                 connectionSocket.getOutputStream());


         // retrieve first line of request and set up for parsing
         requestMessageLine = inFromClient.readLine();
         System.out.println(requestMessageLine);

         // get data: ...

         String name = "Apple iPhone 15";
         double price = 1500.0;
         double quantity = 100.0;


         // Send reply

         StringBuffer response = new StringBuffer("<html> <body> <h3> Howdy! Welcome to my homepage! </h3> ");
         response.append("<p> Product ID: " + id + "</p>");
         response.append("<p> Product Name: " + name + "</p>");
         response.append("<p> Price: " + price + "</p>");
         response.append("<p> Quantity: " + quantity + "</p>");
         response.append("</body> </html>");

         outToClient.writeBytes("HTTP/1.1 200 OK\r\n");
         outToClient.writeBytes("Content-Type: text/html\r\n");
         outToClient.writeBytes("Content-Length: " + response.length() + "\r\n");
         outToClient.writeBytes("\r\n");
         outToClient.writeBytes(response.toString());

         // read and print out the rest of the request
         requestMessageLine = inFromClient.readLine();
         while (requestMessageLine.length() >= 5) {
             System.out.println(requestMessageLine);
             requestMessageLine = inFromClient.readLine();
         }
         System.out.println("Request: " + requestMessageLine);

         connectionSocket.close();
        listenSocket.close();    
     }
     
    }
}

      
          
