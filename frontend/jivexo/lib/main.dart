import 'package:flutter/material.dart';

import 'assests/global.dart';
import 'main/home_screen.dart';
import 'main/login.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Jivexo',
      scaffoldMessengerKey: snackbarKey,
      initialRoute: '/',
      routes: {
        '/' : (context) => const HomeScreen(),
        '/sign-in' : (context) => const LoginScreen(),
      },
    );
  }
}

