import socket
import concurrent.futures
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QWidget,
    QProgressBar,
    QHBoxLayout,
    QComboBox,
)

# Dicionário com algumas portas e serviços conhecidos
WELL_KNOWN_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    119: "NNTP (Usenet)",
    123: "NTP (Network Time Protocol)",
    135: "RPC Endpoint Mapper",
    137: "NetBIOS Name Service",
    138: "NetBIOS Datagram Service",
    139: "NetBIOS Session Service",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP Trap",
    179: "BGP (Border Gateway Protocol)",
    194: "IRC (Internet Relay Chat)",
    389: "LDAP",
    443: "HTTPS",
    445: "Microsoft-DS (AD, SMB)",
    465: "SMTPS (Secure SMTP)",
    515: "LPD (Line Printer Daemon)",
    587: "SMTP (Submission)",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
}

class PortScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Port Scanner - Simples")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label_info = QLabel("Digite IP ou domínio:")
        layout.addWidget(self.label_info)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Exemplo: scanme.nmap.org ou 192.168.1.1")
        layout.addWidget(self.host_input)

        port_layout = QHBoxLayout()
        self.start_port_input = QLineEdit()
        self.start_port_input.setPlaceholderText("Porta inicial (Ex: 20)")
        self.end_port_input = QLineEdit()
        self.end_port_input.setPlaceholderText("Porta final (Ex: 100)")

        port_layout.addWidget(self.start_port_input)
        port_layout.addWidget(self.end_port_input)
        layout.addLayout(port_layout)

        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP"])
        layout.addWidget(self.protocol_combo)

        self.scan_button = QPushButton("Iniciar Escaneamento")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Apenas Abertas", "Apenas Fechadas", "Apenas Filtradas"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_combo)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["Porta", "Status", "Serviço"])
        layout.addWidget(self.result_table)

        self.label_status = QLabel("")
        layout.addWidget(self.label_status)

    def start_scan(self):
        host = self.host_input.text().strip()
        protocol = self.protocol_combo.currentText()
        try:
            start_port = int(self.start_port_input.text())
            end_port = int(self.end_port_input.text())
        except ValueError:
            self.label_status.setText("Erro: Insira portas válidas.")
            return
        
        ports = range(start_port, end_port + 1)
        total_ports = len(ports)

        self.result_table.setRowCount(0)
        self.progress_bar.setMaximum(total_ports)
        self.progress_bar.setValue(0)

        scan_results = []
        self.label_status.setText("Escaneando...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.scan_port, host, port, protocol): port for port in ports}
            
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                status, banner = future.result()
                scan_results.append((port, status, banner))
                self.progress_bar.setValue(self.progress_bar.value() + 1)
                QtWidgets.QApplication.processEvents()

        scan_results.sort(key=lambda x: x[0])
        for port, status, banner in scan_results:
            service = WELL_KNOWN_PORTS.get(port, "Desconhecido")
            if banner and banner != "N/A":
                service = f"{service} - {banner}"
            self.add_result(port, status, service)

        self.label_status.setText(f"Escaneamento concluído! {total_ports} portas verificadas.")

    def scan_port(self, host, port, protocol):
        if protocol == "TCP":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.settimeout(1.5)
        try:
            if protocol == "TCP":
                sock.connect((host, port))
                sock.sendall(b"Hello\r\n")
            else:
                sock.sendto(b"Hello", (host, port))
                sock.recvfrom(1024)
            banner = sock.recv(1024).decode(errors="ignore").strip() if protocol == "TCP" else "N/A"
            return "Aberta", banner if banner else ""
        except socket.timeout:
            return "Filtrada", ""
        except socket.error:
            return "Fechada", ""
        finally:
            sock.close()

    def add_result(self, port, status, service):
        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)
        self.result_table.setItem(row_position, 0, QTableWidgetItem(str(port)))
        self.result_table.setItem(row_position, 1, QTableWidgetItem(status))
        self.result_table.setItem(row_position, 2, QTableWidgetItem(service))

    def apply_filter(self):
        selected = self.filter_combo.currentText()
        for row in range(self.result_table.rowCount()):
            status_item = self.result_table.item(row, 1)
            self.result_table.setRowHidden(row, False)

            if selected == "Apenas Abertas" and status_item.text() != "Aberta":
                self.result_table.setRowHidden(row, True)
            elif selected == "Apenas Fechadas" and status_item.text() != "Fechada":
                self.result_table.setRowHidden(row, True)
            elif selected == "Apenas Filtradas" and status_item.text() != "Filtrada":
                self.result_table.setRowHidden(row, True)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PortScannerApp()
    window.show()
    sys.exit(app.exec_())
