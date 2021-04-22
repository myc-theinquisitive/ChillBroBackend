<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Invoice</title>
  <!-- Tell the browser to be responsive to screen width -->
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Font Awesome -->
  <link rel="stylesheet" href="plugins/fontawesome-free/css/all.min.css">
  <!-- Ionicons -->
  <link rel="stylesheet" href="https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css">
  <!-- Theme style -->
  <link rel="stylesheet" href="dist/css/adminlte.min.css">
  <!-- Google Font: Source Sans Pro -->
  <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700" rel="stylesheet">
</head>
<body class="hold-transition sidebar-mini">
<div class="wrapper">
  <!-- Navbar -->



  <!-- Content Wrapper. Contains page content -->
  <div class="content-wrapper">
    <!-- Content Header (Page header) -->
    <section class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6">
            <h1>Invoice</h1>
          </div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a href="#">Home</a></li>
              <li class="breadcrumb-item active">Invoice</li>
            </ol>
          </div>
        </div>
      </div><!-- /.container-fluid -->
    </section>

    <div><span>DATE:</span> {{booking_date}}</div>
      <div><span>Booking ID:</span> {{booking_id}}</div>
      <div><span>status ID:</span> {{booking_status}}</div>

    <section class="content">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="callout callout-info">
              <h5><i class="fas fa-info"></i> Note:</h5>
              This page has been enhanced for printing. Click the print button at the bottom of the invoice to test.
            </div>


            <!-- Main content -->
            <div class="invoice p-3 mb-3">
              <!-- title row -->
              <div class="row">
                <div class="col-12">
                  <h4>
                    <i class="fas fa-globe"></i> <br>
                    Adinos, contact address, phone no, mail id
                    <small class="float-right">Ordered Date:
                    <?
                        $date=explode(" ",$order_data[0])[0];
                        echo $date;
                    ?></small>
                  </h4>
                </div>
                <!-- /.col -->
              </div>
              <!-- info row -->
              <div class="row invoice-info">
                <div class="col-sm-4 invoice-col">
                  <h5>Location Billing Address</h5>
                  <address>
                    <strong><? echo $hub_admin_data[0]; ?></strong><br>
                    <?
                        echo "Door No: ".$hub_data[2].",".$hub_data[3]."<br>";
                        echo $hub_data[4].",".$hub_data[5]."<br>";
                        if(strlen($hub_data[6])>0)
                        echo $hub_data[7].",".$hub_data[6]."<br>";
                        echo $hub_data[1]."<br>";
                    ?>
                    Phone: <? echo $hub_admin_data[1]; ?><br>
                    Email: <? echo $hub_admin_data[2]; ?>
                  </address>
                </div>
                <!-- /.col -->
                <div class="col-sm-4 invoice-col">
                  <h5>Shipping Address</h5>
                  <address>
                    <strong><? echo ucfirst($user_data[0]); ?></strong><br>
                    <?
                        echo "Door No: ".$user_address[1].",".$user_address[2]."<br>";
                        echo $user_address[3].",".$user_address[4]."<br>";
                        if(strlen($user_address[6])>0)
                        echo $user_address[6].",".$user_address[5]."<br>";
                        echo $user_address[0]."<br>";
                    ?>
                    Phone: <? echo $user_data[2]; ?><br>
                    Email: <? echo $user_data[1]; ?>
                  </address>
                </div>
                <!-- /.col -->
                <div class="col-sm-4 invoice-col">
                  <b>Invoice:</b><? echo $order_data[12]; ?><br>
                  <br>
                  <b>Order ID:</b> <? echo $order_id; ?><br>
                  <b>Payment Due:</b> <? echo  $date; ?><br>
                  <!--<b>Account:</b> 968-34567-->
                </div>
                <!-- /.col -->
              </div>
              <!-- /.row -->

              <!-- Table row -->
              <br><br>
              <div class="row">
                <div class="col-12 table-responsive">
                  <table class="table table-striped"  >
                    <thead class="bg-dark" align="center">
                    <tr>
                      <th>S No</th>
                      <th>Product Name</th>
                      <th>Unit Price</th>
                      <th>Quantity</th>
                      <th>Discount</th>
                      <th>Actual Price</th>
                      <th>Discounted Price</th>
                    </tr>
                    </thead>
                    <tbody align="center">
                        <?  $sub_total=0;
                            $actual_total1=0;
                            for($i=1;$i<=$product_data->num_rows;$i++){
                                $row=$product_data->fetch_array(MYSQLI_NUM);
                        ?>
                            <tr>
                                <td><? echo $i; ?></td>
                                <td><? echo $row[0]; ?></td>
                                <td><? echo $row[4]; ?></td>
                                <td><? echo $row[3]; ?></td>
                                <td><? echo $row[5]; ?></td>
                                <td><? $actual_total=intval($row[3])*intval($row[4]);
                                        $actual_total1+=$actual_total;
                                        echo $actual_total;
                                    ?>
                                </td>
                                <td><?
                                        if(intval($row[5])!=0)
                                            $total=(intval($row[3])*intval($row[4]))-(intval($row[3])*intval($row[4])*intval($row[5])/100);
                                        else
                                            $total=intval($row[3])*intval($row[4]);
                                    $sub_total+=$total;
                                    echo $total;
                                    ?></td>
                            </tr>
                        <?
                            }
                        ?>

                    </tbody>
                  </table>
                </div>
                <!-- /.col -->
              </div>
              <!-- /.row -->
              <br><br>
              <div class="row">
                <!-- accepted payments column -->
                <div class="col-6">
                  <p class="lead">Payment Methods:</p>
                  <img src="dist/img/credit/visa.png" alt="Visa">
                  <img src="dist/img/credit/mastercard.png" alt="Mastercard">
                  <img src="dist/img/credit/american-express.png" alt="American Express">
                  <img src="dist/img/credit/paypal2.png" alt="Paypal">

                  <p class="text-muted well well-sm shadow-none" style="margin-top: 10px;">
                    Etsy doostang zoodles disqus groupon greplin oooj voxy zoodles, weebly ning heekya handango imeem
                    plugg
                    dopplr jibjab, movity jajah plickers sifteo edmodo ifttt zimbra.
                  </p>
                </div>
                <!-- /.col -->
                <div class="col-6">
                  <!--<p class="lead">Amount Due 2/22/2014</p>-->

                  <div class="table-responsive">
                    <table class="table">
                      <tr>
                        <th style="width:50%">Subtotal:</th>
                        <td><? echo $actual_total1; ?></td>
                      </tr>
                      <tr>
                        <th>Shipping:</th>
                        <td><? echo "+".$order_data[11]; ?></td>
                      </tr>
                      <tr>
                        <th>Discount:</th>
                        <td><? echo "-".($actual_total1-$sub_total); ?></td>
                      </tr>
                      <tr style="border-top:2px solid">
                        <th>Total:</th>
                        <td><? echo $sub_total+intval($order_data[11]); ?></td>
                      </tr>
                    </table>
                  </div>
                </div>
                <!-- /.col -->
              </div>
              <!-- /.row -->

              <!-- this row will not appear when printing -->
              <div class="row no-print">
                <div class="col-12">
                  <a href="pages/examples/InvoicePrint.php?order_id=<? echo $order_id; ?>" target="_blank" class="btn btn-primary float-right"><i class="fas fa-print"></i> Print</a>
                </div>
              </div>
            </div>
            <!-- /.invoice -->
          </div><!-- /.col -->
        </div><!-- /.row -->
      </div><!-- /.container-fluid -->
    </section>
    <!-- /.content -->
  </div>
  <!-- /.content-wrapper -->
  <footer class="main-footer no-print">
    <div class="float-right d-none d-sm-block">
      <b>Version</b> 3.0.5
    </div>
    <strong>Copyright &copy; 2014-2019 <a href="https://theinquisitive.in">TheInquisitive</a>.</strong> All rights
    reserved.
  </footer>

  <!-- Control Sidebar -->
  <aside class="control-sidebar control-sidebar-dark">
    <!-- Control sidebar content goes here -->
  </aside>
  <!-- /.control-sidebar -->
</div>
<!-- ./wrapper -->

<!-- jQuery -->
<script src="plugins/jquery/jquery.min.js"></script>
<!-- Bootstrap 4 -->
<script src="plugins/bootstrap/js/bootstrap.bundle.min.js"></script>
<!-- AdminLTE App -->
<script src="dist/js/adminlte.min.js"></script>
<!-- AdminLTE for demo purposes -->
<script src="dist/js/demo.js"></script>
</body>
</html>
